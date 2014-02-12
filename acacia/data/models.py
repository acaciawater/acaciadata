import os,datetime
from django.db import models
from django.db.models import Avg, Max, Min
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.utils import timezone
from acacia import settings
import math
import binascii
#from autoslug.fields import AutoSlugField

import logging
logger = logging.getLogger(__name__)

def project_upload(instance, filename):
    return '/'.join(['images', instance.name, filename])

class Project(models.Model):
    name = models.CharField(max_length=50)
#    slug = AutoSlugField(populate_from='name',null=True, blank=True, default='slug')
    description = models.TextField(blank=True,verbose_name='omschrijving')
    image = models.ImageField(upload_to=project_upload, blank = True, null=True)
    
    def locaties(self):
        return self.projectlocatie_set.count()
    
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'projecten'

def locatie_upload(instance, filename):
    return '/'.join(['images', instance.project.name, instance.name, filename])

class ProjectLocatie(models.Model):
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=50,verbose_name='naam')
#    slug = AutoSlugField(populate_from='name',null=True, blank=True, default='slug')
    description = models.TextField(blank=True,verbose_name='omschrijving')
    xcoord = models.FloatField()
    ycoord = models.FloatField()
    image = models.ImageField(upload_to=locatie_upload, blank = True, null = True)

    def meetlocaties(self):
        return self.meetlocatie_set.count()

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name',]

def meetlocatie_upload(instance, filename):
    return '/'.join(['images', instance.project.name, instance.projectlocatie.name, instance.name, filename])

class MeetLocatie(models.Model):
    projectlocatie = models.ForeignKey(ProjectLocatie)
    name = models.CharField(max_length=50,verbose_name='naam')
#    slug = AutoSlugField(populate_from='name',null=True, blank=True, default='slug')
    description = models.TextField(blank=True,verbose_name='omschrijving')
    xcoord = models.FloatField()
    ycoord = models.FloatField()
    image = models.ImageField(upload_to=meetlocatie_upload, blank = True, null = True)

    def project(self):
        return self.projectlocatie.project
        
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name',]
        
def classForName( kls ):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)            
    return m

class Generator(models.Model):
    name = models.CharField(max_length=50,verbose_name='naam')
    classname = models.CharField(max_length=50,verbose_name='python klasse naam',
                                 help_text='volledige naam van de generator klasse, bijvoorbeeld acacia.data.generators.knmi')
    description = models.TextField(blank=True,verbose_name='omschrijving')
    
    def get_class(self):
        return classForName(self.classname)
    
    def __unicode__(self):
        return self.name
    
class DataFile(models.Model):
    name = models.CharField(max_length=50,verbose_name='naam')
#    slug = AutoSlugField(populate_from='name',null=True, blank=True, default='slug')
    description = models.TextField(blank=True,verbose_name='omschrijving')
    meetlocaties=models.ManyToManyField(MeetLocatie,related_name='datafiles',help_text='meetlocaties die gebruik maken van deze datafile')
    file=models.FileField(upload_to='datafiles',blank=True)
    url=models.CharField(blank=True,max_length=200,help_text='volledige url van de remote file. Leeg laten voor handmatige uploads')
    generator=models.ForeignKey(Generator,blank=True, null=True,help_text='Generator voor het maken van tijdseries uit de datafile')
    created = models.DateTimeField(auto_now_add=True)
    uploaded = models.DateTimeField(auto_now=True)
    user=models.ForeignKey(User,default=User)
    crc=models.IntegerField()

    #@property
    def filename(self):
        return os.path.basename(self.file.name)
    filename.short_description = 'bestandsnaam'

    def compute_crc(self):
        crc = abs(binascii.crc32(self.file.read()))
        return crc
    
    #@property
    def filesize(self):
        try:
            return os.path.getsize(os.path.join(settings.MEDIA_ROOT,self.file.name))
        except:
            # file may not (yet) exist
            return ''
    filesize.short_description = 'grootte'

    #@property
    def filedate(self):
        try:
            return datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(settings.MEDIA_ROOT,self.file.name)))
        except:
            # file may not (yet) exist
            return ''
    filedate.short_description = 'datum'
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return r'/data/%i/' % self.id 
    
    def get_generator_instance(self):
        gen = self.generator.get_class()
        return gen()
    
    def download(self,save=True):
        if self.generator is None:
            logger.error('Cannot download datafile %s: no generator defined' % (self.name))
            return;

        logger.info('Downloading datafile %s from %s' % (self.name, self.url))
        gen = self.get_generator_instance()
        if gen is None:
            logger.error('Cannot download datafile %s: could not create instance of generator %s' % (self.name, self.generator))
            return;

        filename, response = gen.download(url=self.url)
        if response is None:
            logger.error('No response from server')
        elif len(response) == 0:
            logger.warning('Empty response received from server, download aborted')
        else:
            logger.info('Download completed, got file %s', filename)
            new_crc = abs(binascii.crc32(response))
            if self.crc == new_crc:
                logger.warning('Downloaded file %s appears to be identical to local file %s' % (filename, self.file))
            else:
                self.file.save(name=filename, content=ContentFile(response), save=save)
                logger.info('File saved as %s (size = %d)', self.filename(), self.filesize())
                
    def update_parameters(self):
        logger.info('Updating parameters for datafile %s' % self.name)
        gen = self.get_generator_instance()
        params = gen.get_parameters(self.file)
        self.file.close()
        logger.info('Update completed, got %d parameters', len(params))
        num_created = 0
        num_updated = 0
        for p in params:
            param, created = self.parameter_set.get_or_create(name=p['name'], defaults=p)
            if created:
                num_created = num_created+1
            else:
                num_updated = num_updated+1
        logger.info('%d parameters created, %d updated' % (num_created, num_updated))
        
    def get_data(self,**kwargs):
        logger.info('Getting data from datafile %s', self.name)
        gen = self.get_generator_instance()
        self.file.open('r')
        data = gen.get_data(self.file,**kwargs)
        self.file.close()
        if data is None:
            logger.warning('No data retrieved from %s' % self.name)
        else:
            shape = data.shape
            logger.info('Got %d rows, %d columns', shape[0], shape[1])
        return data
    
    def parameters(self):
        return self.parameter_set.count()
    
from django.db.models.signals import pre_delete, pre_save
from django.dispatch.dispatcher import receiver

@receiver(pre_delete, sender=DataFile)
def datafile_delete(sender, instance, **kwargs):
    logger.info('Deleting file %s for datafile %s' % instance.file.name, instance.name)
    instance.file.delete(False)
    logger.info('File %s deleted' % instance.file.name)

@receiver(pre_save, sender=DataFile)
def datafile_save(sender, instance, **kwargs):
    if instance.url != '':
        instance.download(False)

def thumb_upload(instance, filename):
    return '/'.join(['datafiles/thumb', instance.datafile.name, filename])

SERIES_CHOICES = (('line', 'lijn'),
                  ('column', 'staaf'),
                  ('scatter', 'punt'),
                  ('area', 'vlak'),
                  )

from matplotlib import rcParams
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Tahoma']
rcParams['font.size'] = '8'

import matplotlib.pyplot as plt
        
class Parameter(models.Model):
    datafile = models.ForeignKey(DataFile)
    name = models.CharField(max_length=50,verbose_name='naam')
 #   slug = AutoSlugField(populate_from='name',null=True, blank=True, default='slug')
    description = models.TextField(blank=True,verbose_name='omschrijving')
    unit = models.CharField(max_length=10, default='m',verbose_name='eenheid')
    type = models.CharField(max_length=20, default='line', choices = SERIES_CHOICES)
    thumbnail = models.ImageField(upload_to=thumb_upload, blank=True, null=True)

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.datafile)

    def get_data(self):
        return self.datafile.get_data(param=self.name)

    def thumb(self):
        update_needed = True
        try:
            dafile = os.path.join(settings.MEDIA_ROOT,self.datafile.file.name)
            imfile = os.path.join(settings.MEDIA_ROOT,self.thumbnail.file.name)
            update_needed = os.path.getmtime(dafile) > os.path.getmtime(imfile)
        except:
            update_needed = True
        if update_needed:
            self.make_thumbnail()
        return self.thumbnail

    def thumbtag(self):
        
        try:
            url = "/media/%s" % self.thumbnail.name
        except:
            url = '#'
        tag = '<a href="%s"><img src="%s" height="50px"\></a>' % (url, url)
        return tag
    
    thumbtag.allow_tags=True
    thumbtag.short_description='thumbnail'
    
    def make_thumbnail(self):
        #matplotlib.rcParams.update({'font.size': 8})
        data = self.get_data()
        logger.debug('Generating thumbnail for parameter %s' % self.name)
        series = data[self.name]
        try:
            plt.figure()
            options = {'figsize': (6,2), 'grid': False, 'xticks': [], 'legend': False}
            if self.type == 'column':
                series.plot(kind='bar', **options)
            elif self.type == 'area':
                x = series[0]
                y = series[1]
                series.plot(**options)
                plt.fill_between(x,y.min(),y,alpha=0.5)
            else:
                series.plot(**options)
            
            dest =  thumb_upload(self, self.name+'.png')
            imagefile = os.path.join(settings.MEDIA_ROOT, dest)
            imagedir = os.path.dirname(imagefile)
            if not os.path.exists(imagedir):
                os.makedirs(imagedir)
            plt.savefig(imagefile)
            logger.info('Generated thumbnail %s' % dest)
            self.thumbnail.name = dest
        except Exception as e:
            logger.error('Error generating thumbnail: %s: %s' % (e, e.args))
        return self.thumbnail
    
@receiver(pre_save, sender=Parameter)
def parameter_save(sender, instance, **kwargs):
    instance.make_thumbnail()

class Series(models.Model):
    name = models.CharField(max_length=50,verbose_name='naam')
 #   slug = AutoSlugField(populate_from='name',null=True, blank=True, default='slug')
    description = models.TextField(blank=True,verbose_name='omschrijving')
    unit = models.CharField(max_length=10, blank=True, verbose_name='eenheid')
    parameter = models.ForeignKey(Parameter,null=True,blank=True)
    type = models.CharField(max_length=20, default='line', choices = SERIES_CHOICES)
# TODO: aggragatie toevoegen , e.g [avg, hour] or totals per day: [sum,day]
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return r'/series/%i/' % self.id 

    def datafile(self):
        return self.parameter.datafile

    def update(self):
        logger.info('Updating series %s' % self.name)
        data = self.parameter.get_data()
        series = data[self.parameter.name]
        tz = timezone.get_current_timezone()
        num_bad = 0
        num_created = 0
        num_updated = 0
        for date,value in series.iteritems():
            try:
                value = float(value)
                if not (math.isnan(value) or date is None):
                    adate = timezone.make_aware(date,tz)
                    point, created = self.datapoints.get_or_create(date=adate, defaults={'value': value})
                    if created:
                        num_created = num_created+1
                    else:
                        num_updated = num_updated+1
            except:
                num_bad = num_bad+1
                pass
        logger.info('Series %s updated: %d points created, %d updated, %d skipped' % (self.name, num_created, num_updated, num_bad))

    def aantal(self):
        return self.datapoints.count()
    
    def van(self):
        van = datetime.datetime.now()
        agg = self.datapoints.aggregate(van=Min('date'))
        return agg.get('van', van)

    def tot(self):
        tot = datetime.datetime.now()
        agg = self.datapoints.aggregate(tot=Max('date'))
        return agg.get('van', tot)
    
    def minimum(self):
        agg = self.datapoints.aggregate(min=Min('value'))
        return agg.get('min', 0)

    def maximum(self):
        agg = self.datapoints.aggregate(max=Max('value'))
        return agg.get('max', 0)

    def gemiddelde(self):
        agg = self.datapoints.aggregate(avg=Avg('value'))
        return agg.get('avg', 0)
        
    def replace(self):
        logger.info('Deleting all %d datapoints from series %s' % (self.datapoints.count(), self.name))
        self.datapoints.all().delete()
        self.update()
        
    class Meta:
        verbose_name = 'tijdreeks'
        verbose_name_plural = 'tijdreeksen'

        
class DataPoint(models.Model):
    series = models.ForeignKey(Series,related_name='datapoints')
    date = models.DateTimeField()
    value = models.FloatField()
    def jdate(self):
        return self.date.date

class Chart(models.Model):
    series = models.ManyToManyField(Series)
    name = models.CharField(max_length = 50, verbose_name = 'naam')
#   slug = AutoSlugField(populate_from='name',null=True, blank=True, default='slug')
    title = models.CharField(max_length = 50, verbose_name = 'titel')
    type = models.CharField(max_length=20, default='line', choices = SERIES_CHOICES)

    def tijdreeksen(self):
        return self.series.count()
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Grafiek'
        verbose_name_plural = 'Grafieken'