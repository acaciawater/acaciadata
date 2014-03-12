import os,datetime,math,binascii
from django.db import models, transaction
from django.db.models import Avg, Max, Min, Sum
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

    def datasourcecount(self):
        return self.datasources.count()
    datasourcecount.short_description = 'Aantal datasources'

    def get_absolute_url(self):
        return reverse('meetlocatie-detail',args=[self.id])
    
    def __unicode__(self):
        return '%s %s' % (self.projectlocatie, self.name)

    class Meta:
        ordering = ['name',]
        unique_together = ('projectlocatie', 'name')

    def series(self):
        ser = []
        for f in self.datasources.all():
            for p in f.parameter_set.all():
                for s in p.series_set.all():
                    ser.append(s)
        return ser

    def charts(self):
        charts = []
        for f in self.datasources.all():
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
        
class Datasource(models.Model):
    name = models.CharField(max_length=50,verbose_name='naam')
    description = models.TextField(blank=True,verbose_name='omschrijving')
    meetlocatie=models.ForeignKey(MeetLocatie,related_name='datasources',help_text='Meetlocatie van deze gegevensbron')
    url=models.CharField(blank=True,max_length=200,help_text='volledige url van de gegevensbron. Leeg laten voor handmatige uploads')
    generator=models.ForeignKey(Generator,help_text='Generator voor het maken van tijdseries')
    created = models.DateTimeField(auto_now_add=True)
    last_download = models.DateTimeField(null=True, blank=True, verbose_name='laatste download')
    user=models.ForeignKey(User,default=User)
    config=models.TextField(blank=True,null=True,default='{}',verbose_name = 'Additionele configuraties',help_text='Geldige JSON dictionary')
    username=models.CharField(max_length=20, blank=True, default='anonymous', verbose_name='Gebuikersnaam',help_text='Gebruikersnaam voor downloads')
    password=models.CharField(max_length=20, blank=True, verbose_name='Wachtwoord',help_text='Wachtwoord voor downloads')

    class Meta:
        unique_together = ('name', 'meetlocatie',)
        verbose_name = 'gegevensbron'
        verbose_name_plural = 'gegevensbronnen'
        
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('datasource-detail', args=[self.id]) 
    
    def get_generator_instance(self):
        if self.generator is None:
            raise Exception('Generator not defined for datasource %s' % self.name)
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
            logger.error('Cannot download datasource %s: no url supplied' % (self.name))
            return 0

        if self.generator is None:
            logger.error('Cannot download datasource %s: no generator defined' % (self.name))
            return 0
            
        logger.info('Downloading datasource %s from %s' % (self.name, self.url))
        gen = self.get_generator_instance()
        if gen is None:
            logger.error('Cannot download datasource %s: could not create instance of generator %s' % (self.name, self.generator))
            return 0
        
        options = {'url': self.url}
        if self.username is not None and self.username != '':
            options['username'] = self.username
            options['password'] = self.password
        try:
            # merge options with config
            config = json.loads(self.config)
            options = dict(options.items() + config.items())
        except Exception as e:
            logger.error('Cannot download datasource %s: error in config options. %s' % (self.name, e))
            return 0
        
        try:
            results = gen.download(**options)
        except Exception as e:
            logger.error('Error downloading datasource %s: %s' % (self.name, e))
            return 0
            
        if results is None:
            logger.error('No response from server')
            return 0
        elif results == {}:
            logger.warning('Empty response received from server, download aborted')
            return 0
        else:
            downloaded = 0
            logger.info('Download completed, got %s file(s)', len(results))
            for filename, content in results.iteritems():
                try:
                    sourcefile = self.sourcefiles.get(name=filename)
                    created = False
                except:
                    sourcefile = SourceFile(name=filename,datasource=self,user=self.user)
                    created = True
                crc = abs(binascii.crc32(content))
                if not created:
                    if sourcefile.crc == crc:
                        logger.warning('Downloaded file %s ignored: identical to local file %s' % (filename, sourcefile.file))
                        continue
                sourcefile.crc = crc
                try:
                    sourcefile.file.save(name=filename, content=ContentFile(content), save=save or created)
                    logger.info('File %s saved to %s' % (filename, sourcefile.filepath()))
                    downloaded += 1
                except Exception as e:
                    logger.error('Error saving sourcefile %s: %s' % (filename, e))
            self.last_download = timezone.now()
            self.save(update_fields=['last_download'])
            return downloaded
        
    def update_parameters(self,data=None):
        logger.info('Updating parameters for datasource %s' % self.name)
        gen = self.get_generator_instance()
        if gen is None:
            return
        params = {}
        for sourcefile in self.sourcefiles.all():
            sourcefile.file.open('r')
            params.update(gen.get_parameters(sourcefile.file))
            sourcefile.file.close()
        logger.info('Update completed, got %d parameters from %d files', len(params),self.sourcefiles.count())
        num_created = 0
        num_updated = 0
        if data is None:
            data = self.get_data()
        for name,defaults in params.iteritems():
            name = name.strip()
            if name == '':
                continue
            try:
                param = self.parameter_set.objects.get(name=name)
                num_updated = num_updated+1
            except:
                param = Parameter(name=name,**defaults)
                param.datasource = self
                num_created = num_created+1
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
        logger.info('Getting data for datasource %s', self.name)
        gen = self.get_generator_instance()
        if gen is None:
            return
        data = None
        for sourcefile in self.sourcefiles.all():
            d = sourcefile.get_data(**kwargs)
            if data is None:
                data = d
            else:
                data = data.append(d)
        # drop duplicate dates (take last)
        if data is not None:
            data = data.groupby(level=0).last()
        return data

    def parametercount(self):
        count = self.parameter_set.count()
        return count if count>0 else None
    parametercount.short_description = 'parameters'

    def filecount(self):
        count = self.sourcefiles.count()
        return count if count>0 else None
    filecount.short_description = 'files'

    def seriescount(self):
        count = sum([p.seriescount() for p in self.parameter_set.all()])
        return count if count>0 else None
    seriescount.short_description = 'tijdreeksen'

    def chartscount(self):
        count = sum([p.chartscount() for p in self.parameter_set.all()])
        return count if count>0 else None
    chartscount.short_description = 'grafieken'

    def start(self):
        agg = self.sourcefiles.aggregate(start=Min('start'))
        return agg.get('start', None)

    def stop(self):
        agg = self.sourcefiles.aggregate(stop=Max('stop'))
        return agg.get('stop', None)

    def rows(self):
        agg = self.sourcefiles.aggregate(rows=Sum('rows'))
        return agg.get('rows', None)
        
class SourceFile(models.Model):
    name=models.CharField(max_length=50)
    datasource = models.ForeignKey('Datasource',related_name='sourcefiles', verbose_name = 'gegevensbron')
    file=models.FileField(upload_to=up.sourcefile_upload,blank=True)
    rows=models.IntegerField(default=0)
    cols=models.IntegerField(default=0)
    start=models.DateTimeField(null=True,blank=True)
    stop=models.DateTimeField(null=True,blank=True)
    crc=models.IntegerField(default=0)
    user=models.ForeignKey(User,default=User)
    created = models.DateTimeField(auto_now_add=True)
    uploaded = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name
     
    class Meta:
        unique_together = ('name', 'datasource',)
        verbose_name = 'bronbestand'
        verbose_name_plural = 'bronbestanden'
     
    def meetlocatie(self):
        return self.datasource.meetlocatie

    def projectlocatie(self):
        return self.datasource.meetlocatie.projectlocatie

    def project(self):
        return self.datasource.meetlocatie.projectlocatie.project
       
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

    def filetag(self):
        return '<a href="%s">%s</a>' % (os.path.join(settings.MEDIA_URL,self.file.name),self.filename())
    filetag.allow_tags=True
    filetag.short_description='bestand'
           
    def get_data(self,gen=None,**kwargs):
        if gen is None:
            gen = self.datasource.get_generator_instance()
        logger.info('Getting data for sourcefile %s', self.name)
        self.file.open('rb')
        data = gen.get_data(self.file,**kwargs)
        self.file.close()
        if data is None:
            logger.warning('No data retrieved from %s' % self.file.name)
        else:
            shape = data.shape
            logger.info('Got %d rows, %d columns', shape[0], shape[1])
        return data

    def get_dimensions(self, gen=None, data=None):
        if gen is None:
            gen = self.datasource.get_generator_instance()
        if data is None:
            data = self.get_data()
        self.rows = data.shape[0]
        self.cols = data.shape[1]
        self.start = data.index.min()
        self.stop = data.index.max()

from django.db.models.signals import pre_delete, pre_save
from django.dispatch.dispatcher import receiver

@receiver(pre_delete, sender=SourceFile)
def sourcefile_delete(sender, instance, **kwargs):
    filename = instance.file.name
    logger.info('Deleting file %s for datafile %s' % (filename, instance.name))
    instance.file.delete(False)
    logger.info('File %s deleted' % filename)

@receiver(pre_save, sender=SourceFile)
def sourcefile_save(sender, instance, **kwargs):
    instance.get_dimensions()
    
SERIES_CHOICES = (('line', 'lijn'),
                  ('column', 'staaf'),
                  ('scatter', 'punt'),
                  ('area', 'vlak'),
                  ('spline', 'spline')
                  )
        
class Parameter(models.Model):
    datasource = models.ForeignKey(Datasource)
    name = models.CharField(max_length=50,verbose_name='naam')
    description = models.TextField(blank=True,verbose_name='omschrijving')
    unit = models.CharField(max_length=10, default='m',verbose_name='eenheid')
    type = models.CharField(max_length=20, default='line', choices = SERIES_CHOICES)
    thumbnail = models.ImageField(upload_to=up.param_thumb_upload, blank=True, null=True)

    def __unicode__(self):
        return '%s - %s' % (self.datasource.name, self.name)

    def meetlocatie(self):
        return self.datasource.meetlocatie

    def projectlocatie(self):
        return self.datasource.meetlocatie.projectlocatie

    def project(self):
        return self.datasource.meetlocatie.projectlocatie.project
    
    def get_data(self):
        return self.datasource.get_data(param=self.name)

    def seriescount(self):
        return self.series_set.count()
    seriescount.short_description='Aantal tijdreeksen'

    def chartscount(self):
        return sum([s.chart_set.count() for s in self.series_set.all()])
    chartscount.short_description='Aantal grafieken'
    
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
            return None
        return self.thumbnail
    
@receiver(pre_delete, sender=Parameter)
def parameter_delete(sender, instance, **kwargs):
    logger.info('Deleting thumbnail %s for parameter %s' % (instance.thumbnail.name, instance.name))
    instance.thumbnail.delete(False)

AXIS_CHOICES = (
                ('l', 'links'),
                ('r', 'rechts'),
               )

class Series(models.Model):
    name = models.CharField(max_length=50,verbose_name='naam')
    description = models.TextField(blank=True,verbose_name='omschrijving')
    unit = models.CharField(max_length=10, blank=True, verbose_name='eenheid')
    parameter = models.ForeignKey(Parameter)
    thumbnail = models.ImageField(upload_to=up.series_thumb_upload, blank=True, null=True)
    user=models.ForeignKey(User,default=User)

    # chart options
    axis = models.IntegerField(default=1,verbose_name='Nummer y-as')
    axislr = models.CharField(max_length=2, choices=AXIS_CHOICES, default='l',verbose_name='Positie y-as')
    color = models.CharField(null=True,blank=True,max_length=16, verbose_name = 'Kleur')
    type = models.CharField(max_length=10, default='line', choices = SERIES_CHOICES)
    label = models.CharField(max_length=20, blank=True,default='')
    y0 = models.FloatField(null=True,blank=True,verbose_name='ymin')
    y1 = models.FloatField(null=True,blank=True,verbose_name='ymax')
    t0 = models.DateTimeField(null=True,blank=True,verbose_name='start')
    t1 = models.DateTimeField(null=True,blank=True,verbose_name='stop')
    
# TODO: aggregatie toevoegen , e.g [avg, hour] or totals per day: [sum,day]
    
    def get_absolute_url(self):
        return reverse('series-detail', args=[self.id]) 

    def datasource(self):
        return self.parameter.datasource

    def meetlocatie(self):
        return self.parameter.datasource.meetlocatie

    def projectlocatie(self):
        return self.parameter.datasource.meetlocatie.projectlocatie

    def project(self):
        return self.parameter.datasource.meetlocatie.projectlocatie.project

    def __unicode__(self):
        return '%s - %s' % (self.datasource(), self.name)

    def create(self, data=None):
        logger.info('Creating series %s' % self.name)
        if data is None:
            data = self.parameter.get_data()
        series = data[self.parameter.name]
        tz = timezone.get_current_timezone()
        num_created = 0
        num_skipped = 0
        for date,value in series.iteritems():
            try:
                value = float(value)
                if not (math.isnan(value) or date is None):
                    adate = timezone.make_aware(date,tz)
                    self.datapoints.create(date=adate, value=value)
                num_created += 1
            except Exception as e:
                logger.debug('Datapoint %s,%g: %s' % (str(date), value, e))
                num_skipped += 1
        logger.info('Series %s updated: %d points created, %d points skipped' % (self.name, num_created, num_skipped))

    def replace(self):
        logger.info('Deleting all %d datapoints from series %s' % (self.datapoints.count(), self.name))
        self.datapoints.all().delete()
        self.create()

    def update(self, data=None):
        logger.info('Updating series %s' % self.name)
        if data is None:
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
                    elif point.value != value:
                        point.value=value
                        point.save(update_fields=['value'])
                        num_updated = num_updated+1
            except Exception as e:
                logger.debug('Problem with datapoint: %s' % e)
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
        return pd.Series(values,index=dates,name=self.name)
    
    def to_csv(self):
        io = StringIO.StringIO()
        ser = self.to_pandas()
        ser.to_csv(io, header=[self.name], index_label='Datum/tijd')
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
            util.save_thumbnail(series, imagefile,self.type)
            logger.info('Generated thumbnail %s' % dest)
            self.thumbnail.name = dest
        except Exception as e:
            logger.error('Error generating thumbnail: %s' % e)
        return self.thumbnail

    class Meta:
        verbose_name = 'tijdreeks'
        verbose_name_plural = 'tijdreeksen'
        unique_together = ('parameter', 'name',)

class DataPoint(models.Model):
    series = models.ForeignKey(Series,related_name='datapoints')
    date = models.DateTimeField()
    value = models.FloatField()
    
    class Meta:
        unique_together=('series','date')

    def jdate(self):
        return self.date.date

class Chart(models.Model):
    series = models.ManyToManyField(Series)
    name = models.CharField(max_length = 50, verbose_name = 'naam')
    title = models.CharField(max_length = 50, verbose_name = 'titel')
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
    