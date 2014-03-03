import os,datetime,math,binascii
from django.db import models
from django.db.models import Avg, Max, Min
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.contrib.gis.db import models as geo
from acacia import settings
import upload as up
import pandas as pd
import json,util
import StringIO

import logging
logger = logging.getLogger(__name__)


THEME_CHOICES = (('dark-blue','blauw'),
                 ('darkgreen','groen'),
                 ('gray','grijs'),
                 ('grid','grid'),
                 ('skies','wolken'),)

class Project(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True,verbose_name='omschrijving')
    image = models.ImageField(upload_to=up.project_upload, blank = True, null=True)
    logo = models.ImageField(upload_to=up.project_upload, blank=True, null=True,help_text='Mini-logo voor grafieken')
    theme = models.CharField(max_length=50,verbose_name='thema', default='dark-blue',choices=THEME_CHOICES,help_text='Thema voor grafieken')
        
    def location_count(self):
        return self.projectlocatie_set.count()
    location_count.short_description='Aantal locaties'
    
    def get_absolute_url(self):
        return reverse('project-detail', args=[self.id])
         
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'projecten'

class ProjectLocatie(geo.Model):
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=50,verbose_name='naam')
    description = models.TextField(blank=True,verbose_name='omschrijving')
    description.allow_tags=True
    image = models.ImageField(upload_to=up.locatie_upload, blank = True, null = True)
    location = geo.PointField(srid=util.RDNEW,verbose_name='locatie', help_text='Projectlocatie in Rijksdriehoekstelsel coordinaten')
    objects = geo.GeoManager()

    def get_absolute_url(self):
        return reverse('projectlocatie-detail', args=[self.id])

    def location_count(self):
        return self.meetlocatie_set.count()
    location_count.short_description='Aantal meetlocaties'

    def __unicode__(self):
        return self.name

    def latlon(self):
        return util.toWGS84(self.location)

    class Meta:
        ordering = ['name',]
        unique_together = ('project', 'name', )

class MeetLocatie(geo.Model):
    projectlocatie = models.ForeignKey(ProjectLocatie)
    name = models.CharField(max_length=50,verbose_name='naam')
    description = models.TextField(blank=True,verbose_name='omschrijving')
    image = models.ImageField(upload_to=up.meetlocatie_upload, blank = True, null = True)
    location = geo.PointField(srid=util.RDNEW,verbose_name='locatie', help_text='Meetlocatie in Rijksdriehoekstelsel coordinaten')
    objects = geo.GeoManager()

    def project(self):
        return self.projectlocatie.project

    def latlon(self):
        return util.toWGS84(self.location)

    def filecount(self):
        return self.datafiles.count()
    filecount.short_description = 'Aantal files'

    def get_absolute_url(self):
        return reverse('meetlocatie-detail',args=[self.id])
    
    def __unicode__(self):
        return '%s %s' % (self.projectlocatie, self.name)

    class Meta:
        ordering = ['name',]
        unique_together = ('projectlocatie', 'name')

    def series(self):
        ser = []
        for f in self.datafiles.all():
            for p in f.parameter_set.all():
                for s in p.series_set.all():
                    ser.append(s)
        return ser

    def charts(self):
        charts = []
        for f in self.datafiles.all():
            for p in f.parameter_set.all():
                for s in p.series_set.all():
                    for c in s.chart_set.all():
                        charts.append(c)
        return charts
        
def classForName( kls ):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)            
    return m

class Generator(models.Model):
    name = models.CharField(max_length=50,verbose_name='naam')
    classname = models.CharField(max_length=50,verbose_name='python klasse',
                                 help_text='volledige naam van de generator klasse, bijvoorbeeld acacia.data.generators.knmi.Meteo')
    description = models.TextField(blank=True,verbose_name='omschrijving')
    
    def get_class(self):
        return classForName(self.classname)
    
    def __unicode__(self):
        return self.name
    
class SourceFile(models.Model):
    group = models.ForeignKey('DataFile')
    file=models.FileField(upload_to=settings.UPLOAD_DATAFILES,blank=True)
    start=models.DateTimeField()
    stop=models.DateTimeField()
    
class DataFile(models.Model):
    name = models.CharField(max_length=50,verbose_name='naam')
    description = models.TextField(blank=True,verbose_name='omschrijving')
    meetlocatie=models.ForeignKey(MeetLocatie,related_name='datafiles',help_text='Meetlocatie van deze datafile')
    file=models.FileField(upload_to=up.datafile_upload,blank=True)
    url=models.CharField(blank=True,max_length=200,help_text='volledige url van de remote file. Leeg laten voor handmatige uploads')
    generator=models.ForeignKey(Generator,help_text='Generator voor het maken van tijdseries uit de datafile')
    created = models.DateTimeField(auto_now_add=True)
    uploaded = models.DateTimeField(auto_now=True)
    user=models.ForeignKey(User,default=User)
    crc=models.IntegerField(default=0)
    config=models.TextField(blank=True,null=True,default='{}',verbose_name = 'Additionele configuraties',help_text='Geldige JSON dictionary')
    username=models.CharField(max_length=20, blank=True, default='anonymous', verbose_name='Gebuikersnaam',help_text='Gebruikersnaam voor webservice')
    password=models.CharField(max_length=20, blank=True, verbose_name='Wachtwoord',help_text='Wachtwoord voor webservice')
    rows=models.IntegerField(default=0)
    cols=models.IntegerField(default=0)
    start=models.DateTimeField(null=True,blank=True)
    stop=models.DateTimeField(null=True,blank=True)

    class Meta:
        unique_together = ('name', 'meetlocatie',)
        
    def filename(self):
        return os.path.basename(self.file.name)
    filename.short_description = 'bestandsnaam'

    def filesize(self):
        try:
            return os.path.getsize(self.filepath())
        except:
            # file may not (yet) exist
            return 0
    filesize.short_description = 'bestandsgrootte'

    def filedate(self):
        try:
            return datetime.datetime.fromtimestamp(os.path.getmtime(self.filepath()))
        except:
            # file may not (yet) exist
            return ''
    filedate.short_description = 'bestandsdatum'

    def filepath(self):
        return os.path.join(settings.MEDIA_ROOT,self.file.name) 
    filedate.short_description = 'bestandslocatie'
       
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('datafile-detail', args=[self.id]) 
    
    def get_generator_instance(self):
        gen = self.generator.get_class()
        if self.config is None or len(self.config)==0:
            return gen()
        else:
            try:
                kwargs = json.loads(self.config)
                return gen(**kwargs)
            except Exception as err:
                logger.error('Configuration error in generator %s: %s' % (self.generator, err))
                return None
    
    def download(self,save=True):
        if self.url is None or len(self.url) == 0:
            logger.error('Cannot download datafile %s: no url supplied' % (self.name))
            return;

        if self.generator is None:
            logger.error('Cannot download datafile %s: no generator defined' % (self.name))
            return;
            
        logger.info('Downloading datafile %s from %s' % (self.name, self.url))
        gen = self.get_generator_instance()
        if gen is None:
            logger.error('Cannot download datafile %s: could not create instance of generator %s' % (self.name, self.generator))
            return;
        options = {'url': self.url}
        if self.username is not None and self.username != '':
            options['username'] = self.username
            options['password'] = self.password
        try:
            # merge options with config
            config = json.loads(self.config)
            options = dict(options.items() + config.items())
        except Exception as e:
            logger.error('Cannot download datafile %s: error in config options. %s' % (self.name, e))
            return
        
        try:
            results = gen.download(**options)
        except Exception as e:
            logger.error('Error downloading datafile %s: %s' % (self.name, e))
            return
            
        if results is None:
            logger.error('No response from server')
        elif results == {}:
            logger.warning('Empty response received from server, download aborted')
        else:
            logger.info('Download completed, got %s files', len(results))
            for filename, content in results.iteritems():
                new_crc = abs(binascii.crc32(content))
                if self.crc == new_crc:
                    logger.warning('Downloaded file %s appears to be identical to local file %s' % (filename, self.file))
                    logger.warning('File not saved')
                else:
                    self.crc = new_crc
                    self.file.save(name=filename, content=ContentFile(content), save=save)
                    logger.info('File %s saved as %s (size = %d)', (filename, self.file, self.filesize()))
                
    def update_parameters(self,data=None):
        logger.info('Updating parameters for datafile %s' % self.name)
        gen = self.get_generator_instance()
        if gen is None:
            return
        self.file.open('r')
        params = gen.get_parameters(self.file)
        self.file.close()
        logger.info('Update completed, got %d parameters', len(params))
        num_created = 0
        num_updated = 0
        if data is None:
            data = self.get_data()
        for p in params:
            param, created = self.parameter_set.get_or_create(name=p['name'], defaults=p)
            if created:
                num_created = num_created+1
            else:
                num_updated = num_updated+1
            param.make_thumbnail(data)
            param.save()
        logger.info('%d parameters created, %d updated' % (num_created, num_updated))

    def replace_parameters(self,data=None):
        self.parameter_set.all().delete()
        self.update_parameters(data)

    def make_thumbnails(self):
        data = self.get_data()
        for p in self.parameter_set.all():
            p.make_thumbnail(data)
            
    def get_data(self,**kwargs):
        logger.info('Getting data from datafile %s', self.name)
        gen = self.get_generator_instance()
        if gen is None:
            return
        self.file.open('r')
        data = gen.get_data(self.file,**kwargs)
        self.file.close()
        if data is None:
            logger.warning('No data retrieved from %s' % self.name)
        else:
            shape = data.shape
            logger.info('Got %d rows, %d columns', shape[0], shape[1])
        return data

    def get_dimensions(self, data=None):
        if data is None:
            data = self.get_data()
        self.rows = data.shape[0]
        self.cols = data.shape[1]
        self.start = data.index[0]
        self.stop = data.index[self.rows-1]
        
    def parameters(self):
        return self.parameter_set.count()
    
from django.db.models.signals import pre_delete, pre_save, post_save
from django.dispatch.dispatcher import receiver

@receiver(pre_delete, sender=DataFile)
def datafile_delete(sender, instance, **kwargs):
    logger.info('Deleting file %s for datafile %s' % (instance.file.name, instance.name))
    instance.file.delete(False)
    logger.info('File %s deleted' % instance.file.name)

@receiver(pre_save, sender=DataFile)
def datafile_save(sender, instance, **kwargs):
    if instance.url != '':
        instance.download(False)
    instance.get_dimensions()
    
@receiver(post_save, sender=DataFile)
def datafile_postsave(sender, instance, **kwargs):
    if instance.file is None or instance.file.name is None or instance.file.name == '':
        return
    instance.replace_parameters()

SERIES_CHOICES = (('line', 'lijn'),
                  ('column', 'staaf'),
                  ('scatter', 'punt'),
                  ('area', 'vlak'),
                  ('spline', 'spline')
                  )
        
class Parameter(models.Model):
    datafile = models.ForeignKey(DataFile)
    name = models.CharField(max_length=50,verbose_name='naam')
    description = models.TextField(blank=True,verbose_name='omschrijving')
    unit = models.CharField(max_length=10, default='m',verbose_name='eenheid')
    type = models.CharField(max_length=20, default='line', choices = SERIES_CHOICES)
    thumbnail = models.ImageField(upload_to=up.param_thumb_upload, blank=True, null=True)

    def __unicode__(self):
        return '%s - %s' % (self.datafile.name, self.name)

    def get_data(self):
        return self.datafile.get_data(param=self.name)

    def thumbtag(self):
        return util.thumbtag(self.thumbnail.name)

    def thumbpath(self):
        return os.path.join(settings.MEDIA_ROOT,self.thumbnail.name)
    
    thumbtag.allow_tags=True
    thumbtag.short_description='thumbnail'
    
    def make_thumbnail(self,data=None):
        if data is None:
            data = self.get_data()
        logger.debug('Generating thumbnail for parameter %s' % self.name)
        dest =  up.param_thumb_upload(self, self.name+'.png')
        imagefile = os.path.join(settings.MEDIA_ROOT, dest)
        imagedir = os.path.dirname(imagefile)
        if not os.path.exists(imagedir):
            os.makedirs(imagedir)
        try:
            series = data[self.name]
            util.save_thumbnail(series,imagefile,self.type)
            logger.info('Generated thumbnail %s' % dest)
            self.thumbnail.name = dest
        except Exception as e:
            logger.error('Error generating thumbnail: %s: %s' % (e, e.args))
        return self.thumbnail
    
@receiver(pre_delete, sender=Parameter)
def parameter_delete(sender, instance, **kwargs):
    logger.info('Deleting thumbnail %s for parameter %s' % (instance.thumbnail.name, instance.name))
    instance.thumbnail.delete(False)

class Series(models.Model):
    name = models.CharField(max_length=50,verbose_name='naam')
    description = models.TextField(blank=True,verbose_name='omschrijving')
    unit = models.CharField(max_length=10, blank=True, verbose_name='eenheid')
    parameter = models.ForeignKey(Parameter)
    type = models.CharField(max_length=20, default='line', choices = SERIES_CHOICES)
    thumbnail = models.ImageField(upload_to=up.series_thumb_upload, blank=True, null=True)
    user=models.ForeignKey(User,default=User)
    
# TODO: aggregatie toevoegen , e.g [avg, hour] or totals per day: [sum,day]
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('series-detail', args=[self.id]) 

    def datafile(self):
        try:
            return self.parameter.datafile
        except:
            return None

    def create(self):
        logger.info('Creating series %s' % self.name)
        data = self.parameter.get_data()
        series = data[self.parameter.name]
        tz = timezone.get_current_timezone()
        num_bad = 0
        num_created = 0
        for date,value in series.iteritems():
            try:
                value = float(value)
                if not (math.isnan(value) or date is None):
                    adate = timezone.make_aware(date,tz)
                    self.datapoints.create(date=adate, value=value)
                    num_created += 1
            except Exception as e:
                logger.debug('Datapoint %s,%g: %s' % (str(date), value, e))
                num_bad += 1
                pass
        logger.info('Series %s updated: %d points created, %d skipped' % (self.name, num_created, num_bad))

    def replace(self):
        logger.info('Deleting all %d datapoints from series %s' % (self.datapoints.count(), self.name))
        self.datapoints.all().delete()
        self.create()

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
        self.save() # makes thumbnail
        logger.info('Series %s updated: %d points created, %d updated, %d skipped' % (self.name, num_created, num_updated, num_bad))

    def aantal(self):
        return self.datapoints.count()
    
    def van(self):
#        return self.datapoints.earliest('date')
        van = datetime.datetime.now()
        agg = self.datapoints.aggregate(van=Min('date'))
        return agg.get('van', van)

    def tot(self):
#        return self.datapoints.latest('date')
        tot = datetime.datetime.now()
        agg = self.datapoints.aggregate(tot=Max('date'))
        return agg.get('tot', tot)
    
    def minimum(self):
        agg = self.datapoints.aggregate(min=Min('value'))
        return agg.get('min', 0)

    def maximum(self):
        agg = self.datapoints.aggregate(max=Max('value'))
        return agg.get('max', 0)

    def gemiddelde(self):
        agg = self.datapoints.aggregate(avg=Avg('value'))
        return agg.get('avg', 0)
        
    def thumbpath(self):
        return os.path.join(settings.MEDIA_ROOT,self.thumbnail.name)
        
    def thumbtag(self):
        return util.thumbtag(self.thumbnail.name)
    
    thumbtag.allow_tags=True
    thumbtag.short_description='thumbnail'

    def to_pandas(self):
        dates = [dp.date for dp in self.datapoints.all()]
        values = [dp.value for dp in self.datapoints.all()]
        return pd.Series(values,index=dates)
    
    def to_csv(self):
        io = StringIO.StringIO()
        self.to_pandas().to_csv(io)
        return io.getvalue()
    
    def make_thumbnail(self):
        logger.debug('Generating thumbnail for series %s' % self.name)
        try:
            if self.datapoints.count() == 0:
                self.create()
            series = self.to_pandas()
            dest =  up.series_thumb_upload(self, self.name+'.png')
            imagefile = os.path.join(settings.MEDIA_ROOT, dest)
            imagedir = os.path.dirname(imagefile)
            if not os.path.exists(imagedir):
                os.makedirs(imagedir)
            util.save_thumbnail(series, imagefile, self.type)
            logger.info('Generated thumbnail %s' % dest)
            self.thumbnail.name = dest
        except Exception as e:
            logger.error('Error generating thumbnail: %s' % e)
        return self.thumbnail

    class Meta:
        verbose_name = 'tijdreeks'
        verbose_name_plural = 'tijdreeksen'

@receiver(post_save, sender=Series)
def series_save(sender, instance, **kwargs):
    if instance.datapoints.count() == 0:
        try:
            instance.create()
            instance.make_thumbnail()
        except Exception as e:
            logger.error('Error generating series: %s' % e)

class DataPoint(models.Model):
    series = models.ForeignKey(Series,related_name='datapoints')
    date = models.DateTimeField()
    value = models.FloatField()
    def jdate(self):
        return self.date.date

AXIS_CHOICES = (
                ('l', 'links'),
                ('r', 'rechts'),
               )

class ChartOptions(models.Model):
    axis = models.IntegerField(default=1,verbose_name='Nummer y-as')
    axislr = models.CharField(max_length=2, choices=AXIS_CHOICES, default='l',verbose_name='Positie y-as')
    color = models.CharField(null=True,max_length=16, verbose_name = 'Kleur')
    min = models.FloatField(null=True)
    max = models.FloatField(null=True)
    start = models.DateTimeField(null=True)
    stop = models.DateTimeField(null=True)

    class Meta:
        verbose_name = 'Grafiekopties'
        verbose_name_plural = 'Grafiekopties'
    
class Chart(models.Model):
    series = models.ManyToManyField(Series)
    name = models.CharField(max_length = 50, verbose_name = 'naam')
    title = models.CharField(max_length = 50, verbose_name = 'titel')
    type = models.CharField(max_length=20, default='line', choices = SERIES_CHOICES)
    options = models.ForeignKey(ChartOptions, blank=True, null=True, verbose_name = 'Grafiekopties')
    user=models.ForeignKey(User,default=User)

    def tijdreeksen(self):
        return self.series.count()
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('chart-detail', args=[self.id])
    
    class Meta:
        verbose_name = 'Grafiek'
        verbose_name_plural = 'Grafieken'

class Dashboard(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, verbose_name = 'omschrijving')
    charts = models.ManyToManyField(Chart, verbose_name = 'grafieken')
    user=models.ForeignKey(User,default=User)

    def grafieken(self):
        return self.charts.count()

    def get_absolute_url(self):
        return reverse('dash-view', args=[self.id]) 

    def __unicode__(self):
        return self.name
    