# -*- coding: utf-8 -*-
import os,datetime,math,binascii
from django.db import models
from django.db.models import Avg, Max, Min, Sum
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.contrib.gis.db import models as geo
from django.utils.text import slugify
from acacia import settings
import upload as up
import numpy as np
import pandas as pd
import json,util
import StringIO
import pytz
import logging
logger = logging.getLogger(__name__)


THEME_CHOICES = (('dark-blue','blauw'),
                 ('darkgreen','groen'),
                 ('gray','grijs'),
                 ('grid','grid'),
                 ('skies','wolken'),)

def aware(d,tz=None):
    ''' utility function to ensure datetime object is offset-aware '''
    if d is not None:
        if timezone.is_naive(d):
            if tz is None or tz == '':
                tz = settings.TIME_ZONE
            if not isinstance(tz, timezone.tzinfo):
                tz = pytz.timezone(tz)
            try:
                return timezone.make_aware(d, tz)            
            except:
#                 pytz.NonExistentTimeError, pytz.AmbiguousTimeError: # CET/CEST transition?
                return timezone.make_aware(d, pytz.utc)            
    return d

class Project(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True,null=True,verbose_name='omschrijving')
    image = models.ImageField(upload_to=up.project_upload, blank = True, null=True)
    logo = models.ImageField(upload_to=up.project_upload, blank=True, null=True,help_text='Mini-logo voor grafieken')
    theme = models.CharField(max_length=50,verbose_name='thema', default='dark-blue',choices=THEME_CHOICES,help_text='Thema voor grafieken')
        
    def location_count(self):
        return self.projectlocatie_set.count()
    location_count.short_description='Aantal locaties'
    
    def get_absolute_url(self):
        return reverse('acacia:project-detail', args=[self.id])
         
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'projecten'

class Webcam(models.Model):
    name = models.CharField(max_length=50,verbose_name='naam')
    description = models.TextField(blank=True,null=True,verbose_name='omschrijving')
    image = models.TextField(verbose_name = 'url voor snapshot')
    video = models.TextField(verbose_name = 'url voor streaming video')
    admin = models.TextField(verbose_name = 'url voor beheer')
    
    def snapshot(self):
        url = self.image
        return '<a href="%s"><img src="%s" height="160px"/></a>' % (url, url)

    snapshot.allow_tags=True

    def __unicode__(self):
        return self.name
    
class ProjectLocatie(geo.Model):
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=50,verbose_name='naam')
    description = models.TextField(blank=True,null=True,verbose_name='omschrijving')
    description.allow_tags=True
    image = models.ImageField(upload_to=up.locatie_upload, blank = True, null = True)
    location = geo.PointField(srid=util.RDNEW,verbose_name='locatie', help_text='Projectlocatie in Rijksdriehoekstelsel coordinaten')
    objects = geo.GeoManager()
    webcam = models.ForeignKey(Webcam, null = True, blank=True)
    dashboard = models.ForeignKey('TabGroup', blank=True, null=True, verbose_name = 'Standaard dashboard')
    
    def get_absolute_url(self):
        return reverse('acacia:projectlocatie-detail', args=[self.id])

    def location_count(self):
        return self.meetlocatie_set.count()
    location_count.short_description='Aantal meetlocaties'

    def __unicode__(self):
        return self.name

    def latlon(self):
        return util.toWGS84(self.location)

    def series(self):
        s = []
        for m in self.meetlocatie_set.all():
            s.extend(m.series())
        return s
    
    class Meta:
        ordering = ['name',]
        unique_together = ('project', 'name', )

class MeetLocatie(geo.Model):
    projectlocatie = models.ForeignKey(ProjectLocatie)
    name = models.CharField(max_length=50,verbose_name='naam')
    description = models.TextField(blank=True,null=True,verbose_name='omschrijving')
    image = models.ImageField(upload_to=up.meetlocatie_upload, blank = True, null = True)
    location = geo.PointField(srid=util.RDNEW,verbose_name='locatie', help_text='Meetlocatie in Rijksdriehoekstelsel coordinaten')
    objects = geo.GeoManager()
    webcam = models.ForeignKey(Webcam, null = True, blank=True)

    def project(self):
        return self.projectlocatie.project

    def latlon(self):
        return util.toWGS84(self.location)

    def datasourcecount(self):
        return self.datasources.count()
    datasourcecount.short_description = 'Aantal datasources'

    def get_absolute_url(self):
        return reverse('acacia:meetlocatie-detail',args=[self.id])
    
    def __unicode__(self):
        return '%s %s' % (self.projectlocatie, self.name)

    class Meta:
        ordering = ['name',]
        unique_together = ('projectlocatie', 'name')

    def filecount(self):
        return sum([d.filecount() for d in self.datasources.all()])

    def paramcount(self):
        return sum([d.parametercount() for d in self.datasources.all()])
    
    def series(self):
        ser = []
        for f in self.datasources.all():
            for p in f.parameter_set.all():
                for s in p.series_set.all():
                    ser.append(s)
        # Ook berekende reeksen!
        for f in self.formula_set.all():
            ser.append(f)
        return ser

    def charts(self):
        charts = []
        for f in self.datasources.all():
            for p in f.parameter_set.all():
                for s in p.series_set.all():
                    for c in s.chartseries_set.all():
                        if not c in charts:
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
    name = models.CharField(max_length=50,verbose_name='naam', unique=True)
    classname = models.CharField(max_length=50,verbose_name='python klasse',
                                 help_text='volledige naam van de generator klasse, bijvoorbeeld acacia.data.generators.knmi.Meteo')
    description = models.TextField(blank=True,null=True,verbose_name='omschrijving')
    
    def get_class(self):
        return classForName(self.classname)
    
    def __unicode__(self):
        return self.name
        
    class Meta:
        ordering = ['name',]

LOGGING_CHOICES = (
                  ('OFF', 'Geen'),
                  ('DEBUG', 'Debug'),
                  ('INFO', 'Informatie'),
                  ('WARNING', 'Waarschuwingen'),
                  ('ERROR', 'Fouten'),
#                  ('CRITICAL', 'Alleen kritieke fouten'),
                  )

class Datasource(models.Model):
    name = models.CharField(max_length=50,verbose_name='naam')
    description = models.TextField(blank=True,null=True,verbose_name='omschrijving')
    meetlocatie=models.ForeignKey(MeetLocatie,related_name='datasources',help_text='Meetlocatie van deze gegevensbron')
    url=models.CharField(blank=True,null=True,max_length=200,help_text='volledige url van de gegevensbron. Leeg laten voor handmatige uploads')
    generator=models.ForeignKey(Generator,help_text='Generator voor het maken van tijdreeksen uit de datafiles')
    user=models.ForeignKey(User,default=User,verbose_name='Aangemaakt door')
    created = models.DateTimeField(auto_now_add=True,verbose_name='Aangemaakt op')
    last_download = models.DateTimeField(null=True, blank=True, verbose_name='geactualiseerd')
    autoupdate = models.BooleanField(default=True)
    config=models.TextField(blank=True,null=True,default='{}',verbose_name = 'Additionele configuraties',help_text='Geldige JSON dictionary')
    username=models.CharField(max_length=50, blank=True, null=True, default='anonymous', verbose_name='Gebuikersnaam',help_text='Gebruikersnaam voor downloads')
    password=models.CharField(max_length=50, blank=True, null=True, verbose_name='Wachtwoord',help_text='Wachtwoord voor downloads')
    timezone=models.CharField(max_length=50, blank=True, default=settings.TIME_ZONE)

    class Meta:
        ordering = ['name',]
        unique_together = ('name', 'meetlocatie',)
        verbose_name = 'gegevensbron'
        verbose_name_plural = 'gegevensbronnen'
        
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('acacia:datasource-detail', args=[self.id]) 
    
    def projectlocatie(self):
        return None if self.meetlocatie is None else self.meetlocatie.projectlocatie

    def project(self):
        loc = self.projectlocatie()
        return None if loc is None else loc.project

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
    
    def download(self, start=None):
        if self.url is None or len(self.url) == 0:
            logger.error('Cannot download datasource %s: no url supplied' % (self.name))
            return None

        if self.generator is None:
            logger.error('Cannot download datasource %s: no generator defined' % (self.name))
            return None
            
        logger.info('Downloading datasource %s from %s' % (self.name, self.url))
        gen = self.get_generator_instance()
        if gen is None:
            logger.error('Cannot download datasource %s: could not create instance of generator %s' % (self.name, self.generator))
            return None
        
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
            return None

        if start is not None:
            # override starting date/time
            options['start'] = start
        elif not 'start' in options:
            # incremental download
            options['start'] = self.stop()
        try:
            files = []
            crcs = {f.crc:f.file for f in self.sourcefiles.all()}

            def callback(filename, contents):
                crc = abs(binascii.crc32(contents))
                if crc in crcs:
                    logger.warning('Downloaded file %s ignored: identical to local file %s' % (filename, crcs[crc].file.name))
                    return
                try:
                    sourcefile = self.sourcefiles.get(name=filename)
                except:
                    sourcefile = SourceFile(name=filename,datasource=self,user=self.user)
                sourcefile.crc = crc
                contentfile = ContentFile(contents)
                try:
                    sourcefile.file.save(name=filename, content=contentfile)
                    logger.info('File %s saved to %s' % (filename, sourcefile.filepath()))
                    crcs[crc] = sourcefile.file
                    files.append(sourcefile)
                except Exception as e:
                    logger.exception('Problem saving file %s: %s', (filename,e))
            options['callback'] = callback
            results = gen.download(**options)

        except Exception as e:
            logger.exception('Error downloading datasource %s: %s' % (self.name, e))
            return None            
        logger.info('Download completed, got %s file(s)', len(results))
        self.last_download = timezone.now()
        self.save(update_fields=['last_download'])
        return files
        
    def update_parameters(self,data=None,files=None,limit=10):
        gen = self.get_generator_instance()
        if gen is None:
            return
        logger.info('Updating parameters for datasource %s' % self.name)
        params = {}
        if files is None:
            files = self.sourcefiles.all()[:limit]; 
        for sourcefile in files:
            try:
                try:
                    params.update(gen.get_parameters(sourcefile.file))
                except Exception as e:
                    logger.exception('Cannot update parameters for sourcefile %s: %s' % (sourcefile, e))
            except Exception as e:
                logger.exception('Cannot open sourcefile %s: %s' % (sourcefile, e))
        logger.info('Update completed, got %d parameters from %d files', len(params),self.sourcefiles.count())
        num_created = 0
        num_updated = 0
#        if data is None:
#            data = self.get_data()
        for name,defaults in params.iteritems():
            name = name.strip()
            if name == '':
                continue
            try:
                param = self.parameter_set.get(name=name)
                num_updated = num_updated+1
            except Parameter.DoesNotExist:
                logger.warning('parameter %s created' % name)
                param = Parameter(name=name,**defaults)
                param.datasource = self
                num_created = num_created+1
            #param.make_thumbnail(data)
            param.save()
        logger.info('%d parameters created, %d updated' % (num_created, num_updated))

    def replace_parameters(self,data=None):
        self.parameter_set.all().delete()
        self.update_parameters(data)

    def make_thumbnails(self, data=None):
        if data is None:
            data = self.get_data()
        for p in self.parameter_set.all():
            p.make_thumbnail(data)
    
    def get_data(self,**kwargs):
        gen = self.get_generator_instance()
        if gen is None:
            return
        logger.info('Getting data for datasource %s', self.name)
        data = None
        start = aware(kwargs.get('start', None))
        stop = aware(kwargs.get('stop', None))
        files = kwargs.get('files', None)
        if files is None:
            files = self.sourcefiles.all()
        for sourcefile in files:
#             if sourcefile.rows == 0:
#                 continue
            if start is not None:
                sstop = aware(sourcefile.stop,self.timezone)
                if sstop is None or sstop < start:
                    continue
            if stop is not None:
                sstart = aware(sourcefile.start,self.timezone)
                if sstart is None or sstart > stop:
                    continue
            d = sourcefile.get_data(**kwargs)
            if d is not None:
                if data is None:
                    data = d
                else:
                    data = data.append(d)
        if data is not None:
            #try:
                date = np.array([aware(d, self.timezone) for d in data.index.to_pydatetime()])
                slicer = None
                if start is not None:
                    if stop is not None:
                        slicer = (date >= start) & (date <= stop) 
                    else:
                        slicer = (date >= start)
                elif stop is not None:
                    slicer = (date <= stop)
                if slicer is not None:
                    data = data[slicer]
                # Don't remove duplicates
                # data = data.groupby(level=0).last()
                return data.sort()
            #except:
                pass
        return data

    def to_csv(self):
        io = StringIO.StringIO()
        df = self.get_data()
        if df is None:
            return None
        df.to_csv(io, index_label='Datum/tijd')
        return io.getvalue()

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

    def getseries(self):
        r = set()
        for p in self.parameter_set.all():
            for s in p.series_set.all():
                r.add(s) 
        return r   
    
    def chartscount(self):
        count = sum([p.chartscount() for p in self.parameter_set.all()])
        return count if count>0 else None
    chartscount.short_description = 'grafieken'

    def start(self):
        agg = self.sourcefiles.aggregate(start=Min('start'))
        return aware(agg.get('start', None))

    def stop(self):
        agg = self.sourcefiles.aggregate(stop=Max('stop'))
        return aware(agg.get('stop', None))

    def rows(self):
        agg = self.sourcefiles.aggregate(rows=Sum('rows'))
        return agg.get('rows', None)

class Notification(models.Model):
    datasource = models.ForeignKey(Datasource,help_text='Gegevensbron welke gevolgd wordt')
    user = models.ForeignKey(User,blank=True,null=True,verbose_name='Gebruiker',help_text='Gebruiker die berichtgeving ontvangt over updates')
    email = models.EmailField(max_length=254,blank=True)
    subject = models.TextField(blank=True,default='acaciadata.com update rapport')
    level = models.CharField(max_length=10,choices = LOGGING_CHOICES, default = 'ERROR', verbose_name='Niveau',help_text='Niveau van berichtgeving')
    active = models.BooleanField(default = True,verbose_name='activeren')

    def __unicode__(self):
        return self.datasource.name

    class Meta:
        verbose_name ='Email berichten'
        verbose_name_plural = 'Email berichten'
    
    
# class UpdateSchedule(models.Model):
#     datasource = models.ForeignKey(Datasource)
#     minute = models.CharField(max_length=2,default='0')
#     hour = models.CharField(max_length=2,default='0')
#     day = models.CharField(max_length=2,default='*')
#     month = models.CharField(max_length=2,default='*')
#     dayofweek = models.CharField(max_length=1,default='*')
#     active = models.BooleanField(default=True)
    
class SourceFile(models.Model):
    name=models.CharField(max_length=50,blank=True)
    datasource = models.ForeignKey('Datasource',related_name='sourcefiles', verbose_name = 'gegevensbron')
    file=models.FileField(max_length=200,upload_to=up.sourcefile_upload,blank=True,null=True)
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
        return self.datasource.projectlocatie()

    def project(self):
        return self.datasource.project()
       
    def filename(self):
        try:
            return os.path.basename(self.file.name)
        except:
            return ''
    filename.short_description = 'bestandsnaam'

    def filesize(self):
        try:
            return self.file.size
            #return os.path.getsize(self.filepath())
        except:
            # file may not (yet) exist
            return 0
    filesize.short_description = 'bestandsgrootte'

    def filedate(self):
        try:
            date = datetime.datetime.fromtimestamp(os.path.getmtime(self.filepath()))
            date = aware(date,timezone.get_current_timezone())
            return date
        except:
            # file may not (yet) exist
            return ''
    filedate.short_description = 'bestandsdatum'

    def filepath(self):
        try:
            return self.file.path
            #return os.path.join(settings.MEDIA_ROOT,self.file.name)
        except:
            return ''
    filedate.short_description = 'bestandslocatie'

    def filetag(self):
        return '<a href="%s">%s</a>' % (os.path.join(settings.MEDIA_URL,self.file.name),self.filename())
    filetag.allow_tags=True
    filetag.short_description='bestand'
           
    def get_data(self,gen=None,**kwargs):
        if gen is None:
            gen = self.datasource.get_generator_instance()
        logger.info('Getting data for sourcefile %s', self.name)
        try:
            data = gen.get_data(self.file,**kwargs)
        except Exception as e:
            logger.exception('Error retrieving data from %s: %s' % (self.file.name, e))
            return None
        if data is None:
            logger.warning('No data retrieved from %s' % self.file.name)
        else:
            shape = data.shape
            logger.info('Got %d rows, %d columns', shape[0], shape[1])
        return data

    def get_dimensions(self, data=None):
        if data is None:
            data = self.get_data()
        if data is None:
            self.rows = 0
            self.cols = 0
            self.start = None
            self.stop = None
        else:
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
    date = instance.filedate()
    if date != '':
        if instance.uploaded is None or date > instance.uploaded:
            instance.uploaded = date
    try:
        instance.get_dimensions(data = kwargs.get('data', None))
    except Exception as e:
        logger.exception('Error getting dimensions while saving sourcefile %s: %s' % (instance, e))
    ds = instance.datasource
    if instance.uploaded is None:
        instance.uploaded = timezone.now()
    if ds.last_download is None:
        ds.last_download = instance.uploaded
    elif ds.last_download < instance.uploaded:
        ds.last_download = instance.uploaded
    ds.save()

SERIES_CHOICES = (('line', 'lijn'),
                  ('column', 'staaf'),
                  ('scatter', 'punt'),
                  ('area', 'vlak'),
                  ('spline', 'spline')
                  )
        
class Parameter(models.Model):
    datasource = models.ForeignKey(Datasource)
    name = models.CharField(max_length=50,verbose_name='naam')
    description = models.TextField(blank=True,null=True,verbose_name='omschrijving')
    unit = models.CharField(max_length=10, default='m',verbose_name='eenheid')
    type = models.CharField(max_length=20, default='line', choices = SERIES_CHOICES)
    thumbnail = models.ImageField(upload_to=up.param_thumb_upload, max_length=200, blank=True, null=True)

    def __unicode__(self):
        return '%s - %s' % (self.datasource.name, self.name)

    class Meta:
        ordering = ['name',]
        unique_together = ('name', 'datasource',)

    def meetlocatie(self):
        return self.datasource.meetlocatie

    def projectlocatie(self):
        return self.datasource.projectlocatie()

    def project(self):
        return self.datasource.project()
    
    def get_data(self,**kwargs):
        return self.datasource.get_data(param=self.name,**kwargs)

    def seriescount(self):
        return self.series_set.count()
    seriescount.short_description='Aantal tijdreeksen'
    
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
        dest =  up.param_thumb_upload(self, slugify(unicode(self.name))+'.png')
        self.thumbnail.name = dest
        imagefile = self.thumbnail.path
        imagedir = os.path.dirname(imagefile)
        if not os.path.exists(imagedir):
            os.makedirs(imagedir)
        try:
            series = data[self.name]
            util.save_thumbnail(series,imagefile,self.type)
            logger.info('Generated thumbnail %s' % dest)
            self.save()
        except Exception as e:
            logger.exception('Error generating thumbnail for parameter %s: %s' % (self.name, e))
            return None
        return self.thumbnail
    
@receiver(pre_delete, sender=Parameter)
def parameter_delete(sender, instance, **kwargs):
    logger.info('Deleting thumbnail %s for parameter %s' % (instance.thumbnail.name, instance.name))
    instance.thumbnail.delete(False)

        
RESAMPLE_METHOD = (
              ('T', 'minuut'),
              ('15T', 'kwartier'),
              ('H', 'uur'),
              ('D', 'dag'),
              ('W', 'week'),
              ('M', 'maand'),
              ('A', 'jaar'),
              )
AGGREGATION_METHOD = (
              ('mean', 'gemiddelde'),
              ('max', 'maximum'),
              ('min', 'minimum'),
              ('sum', 'som'),
              ('diff', 'verschil'),
              ('first', 'eerste'),
              ('last', 'laatste'),
              )
# set  default series type from parameter type in sqlite database: 
# update data_series set type = (select p.type from data_parameter p where id = data_series.parameter_id) 

class Series(models.Model):
    name = models.CharField(max_length=50,verbose_name='naam')
    description = models.TextField(blank=True,null=True,verbose_name='omschrijving')
    unit = models.CharField(max_length=10, blank=True, null=True, verbose_name='eenheid')
    type = models.CharField(max_length=20, blank = True, default='line', choices = SERIES_CHOICES)
    parameter = models.ForeignKey(Parameter, null=True, blank=True)
    thumbnail = models.ImageField(upload_to=up.series_thumb_upload, max_length=200, blank=True, null=True)
    user=models.ForeignKey(User,default=User)

    # Nabewerkingen
    resample = models.CharField(max_length=10,choices=RESAMPLE_METHOD,blank=True, null=True, 
                                verbose_name='frequentie',help_text='Frequentie voor resampling van tijdreeks')
    aggregate = models.CharField(max_length=10,choices=AGGREGATION_METHOD,blank=True, null=True, 
                                 verbose_name='aggregatie', help_text = 'Aggregatiemethode bij resampling van tijdreeks')
    scale = models.FloatField(default = 1.0,verbose_name = 'verschaling', help_text = 'constante factor voor verschaling van de meetwaarden (vóór compensatie)')
    offset = models.FloatField(default = 0.0, verbose_name = 'compensatie', help_text = 'constante compensatie van meetwaarden (ná verschaling)')
    cumsum = models.BooleanField(default = False, verbose_name='accumuleren', help_text = 'reeks transformeren naar accumulatie')
    cumstart = models.DateTimeField(blank = True, null = True, verbose_name='start accumulatie')
    
    class Meta:
        ordering = ['name',]
        unique_together = ('parameter', 'name',)
        verbose_name = 'Reeks'
        verbose_name_plural = 'Reeksen'
        
    def get_absolute_url(self):
        return reverse('acacia:series-detail', args=[self.id]) 

    def datasource(self):
        try:
            p = self.parameter
        except:
            # Parameter defined but does not exist. Database integrity problem!
            return None
        return None if p is None else p.datasource

    def meetlocatie(self):
        d = self.datasource()
        return None if d is None else d.meetlocatie

    def projectlocatie(self):
        l = self.meetlocatie()
        return None if l is None else l.projectlocatie

    def project(self):
        p = self.projectlocatie()
        return None if p is None else p.project

    def theme(self):
        p = self.project()
        return None if p is None else 'themes/%s.js' % p.theme
    
    def default_type(self):
        p = self.parameter
        return 'line' if p is None else p.type

    def __unicode__(self):
        return '%s - %s' % (self.datasource() or '(berekend)', self.name)
    
    def do_postprocess(self, series):
        ''' perform postprocessing of series data like resampling, scaling etc'''
        # remove n/a values and duplicates
        series = series.dropna()
        if series.empty:
            return series
        series = series.groupby(level=0).last()
        if series.empty:
            return series
        if self.resample is not None and self.resample != '':
            try:
                series = series.resample(how=self.aggregate, rule=self.resample)
                if series.empty:
                    return series
            except Exception as e:
                logger.exception('Resampling of series %s failed: %s' % (self.name, e))
                return None

        add_value = 0
        if self.cumsum:
            if self.cumstart is not None:
                #start = series.index.searchsorted(self.cumstart)
                series = series[self.cumstart:]
                if series.empty:
                    return series
            series = series.cumsum()
            if series.empty:
                return series
            if self.aantal() > 0:
                # we hadden al bestaande datapoints in de reeks
                # vind laatste punt van bestaande reeks dat voor begin van nieuwe reeks valt
                start = pd.to_datetime(series.index[0]) #begin nieuwe reeks
                try:
                    before = self.datapoints.filter(date__lt = start).order_by('-date')
                    if before:
                        add_value = before[0].value
                except Exception as e:
                    logger.exception('Accumulation of series %s failed: %s' % (self.name, e))
        if self.scale != 1.0:
            series = series * self.scale
        if self.offset != 0.0:
            series = series + self.offset
        if add_value != 0:
            series = series + add_value
        return series
         
    def get_series_data(self, dataframe, start=None):
        
        if self.parameter is None:
            #raise Exception('Parameter is None for series %s' % self.name)
            return None

        if dataframe is None:
            dataframe = self.parameter.get_data(start=start)
            if dataframe is None:
                return None
            
        if not self.parameter.name in dataframe:
            # maybe datasource has stopped reporting about this parameter?
            msg = 'series %s: parameter %s not found' % (self.name, self.parameter.name)
#             msg = msg + ". Available parameters are: %s" % ','.join(dataframe.columns.values.tolist())
            logger.warning(msg)
#             raise Exception(msg)
            return None
        
        series = dataframe[self.parameter.name]
        series = self.do_postprocess(series)
        if start is not None:
            series = series[start:]
        return series

    def create(self, data=None, thumbnail=True):
        tz = timezone.get_current_timezone()
        num_created = 0
        num_skipped = 0
        datapoints = []
        logger.info('Creating series %s' % self.name)
        series = self.get_series_data(data)
        if series is None:
            logger.error('Creation of series %s failed' % self.name)
            return

        for date,value in series.iteritems():
            try:
                value = float(value)
                if math.isnan(value) or date is None:
                    continue
                if not timezone.is_aware(date):
                    date = timezone.make_aware(date,tz)
                #self.datapoints.create(date=adate, value=value)
                datapoints.append(DataPoint(series=self, date=date, value=value))
                num_created += 1
            except Exception as e:
                logger.debug('Datapoint %s,%g: %s' % (str(date), value, e))
                num_skipped += 1
        self.datapoints.bulk_create(datapoints)
        logger.info('Series %s updated: %d points created, %d points skipped' % (self.name, num_created, num_skipped))
        if thumbnail:
            self.make_thumbnail()
        self.save()
        #self.getproperties()#.update()
        
    def replace(self):
        logger.info('Deleting all %d datapoints from series %s' % (self.datapoints.count(), self.name))
        self.datapoints.all().delete()
        self.create()

    def update(self, data=None, start=None):
        tz = timezone.get_current_timezone()
        num_bad = 0
        num_created = 0
        num_updated = 0
        logger.info('Updating series %s' % self.name)
        series = self.get_series_data(data, start)
        if series is None:
            logger.error('Update of series %s failed' % self.name)
            return
        
        for date,value in series.iteritems():
            try:
                value = float(value)
                if math.isnan(value) or date is None:
                    continue
                if not timezone.is_aware(date):
                    date = timezone.make_aware(date,tz)
                point, created = self.datapoints.get_or_create(date=date, defaults={'value': value})
                if created:
                    num_created = num_created+1
                elif point.value != value:
                    point.value=value
                    point.save(update_fields=['value'])
                    num_updated = num_updated+1
            except Exception as e:
                logger.debug('Datapoint %s,%g: %s' % (str(date), value, e))
                num_bad = num_bad+1
        logger.info('Series %s updated: %d points created, %d updated, %d skipped' % (self.name, num_created, num_updated, num_bad))
        self.make_thumbnail()
        self.save()
        #self.getproperties().update()

# start properties
    def aantal(self):
        return self.datapoints.count()
     
    def van(self):
        van = datetime.datetime.now()
        agg = self.datapoints.aggregate(van=Min('date'))
        return agg.get('van', van)
 
    def tot(self):
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
 
    def laatste(self):
        return self.datapoints.order_by('-date')[0]
 
    def beforelast(self):
        if self.aantal() < 1:
            return None
        if self.aantal() == 1:
            return self.eerste()
        return self.datapoints.order_by('-date')[1]
         
    def eerste(self):
        return self.datapoints.order_by('date')[0]
        
# end properties

#     def getproperties(self):
#         if not hasattr(self,'properties'):
#             props = SeriesProperties.objects.create(series = self)
#             props.update()
#         return self.properties
#     
#     def aantal(self):
#         return self.getproperties().aantal
#     
#     def van(self):
#         return self.getproperties().van
# 
#     def tot(self):
#         return self.getproperties().tot
#    
#     def minimum(self):
#         return self.getproperties().min
# 
#     def maximum(self):
#         return self.getproperties().max
# 
#     def gemiddelde(self):
#         return self.getproperties().gemiddelde
# 
#     def laatste(self):
#         return self.getproperties().laatste
# 
#     def beforelast(self):
#         return self.getproperties().beforelast
#         
#     def eerste(self):
#         return self.getproperties().eerste
         
    def thumbpath(self):
        return self.thumbnail.path
         
    def thumbtag(self):
        return util.thumbtag(self.thumbnail.name)
    
    thumbtag.allow_tags=True
    thumbtag.short_description='thumbnail'

    def filter_points(self, **kwargs):
        start = kwargs.get('start', None)
        stop = kwargs.get('stop', None)
        if start is None and stop is None:
            return self.datapoints.all()
        if start is None:
            start = self.van()
        if stop is None:
            stop = self.tot()
        return self.datapoints.filter(date__range=[start,stop])
    
    def to_pandas(self, **kwargs):
        points = self.filter_points(**kwargs)
        dates = [dp.date for dp in points]
        values = [dp.value for dp in points]
        return pd.Series(values,index=dates,name=self.name)
    
    def to_csv(self, **kwargs):
        ser = self.to_pandas(**kwargs)
        io = StringIO.StringIO()
        ser.to_csv(io, header=[self.name], index_label='Datum/tijd')
        return io.getvalue()
    
    def make_thumbnail(self):
        logger.debug('Generating thumbnail for series %s' % self.name)
        try:
            if self.datapoints.count() == 0:
                self.create(thumbnail=False)
            series = self.to_pandas()
            dest =  up.series_thumb_upload(self, slugify(unicode(self.name))+'.png')
            self.thumbnail.name = dest
            imagefile = self.thumbnail.path #os.path.join(settings.MEDIA_ROOT, dest)
            imagedir = os.path.dirname(imagefile)
            if not os.path.exists(imagedir):
                os.makedirs(imagedir)
            util.save_thumbnail(series, imagefile, self.type)
            logger.info('Generated thumbnail %s' % dest)

        except Exception as e:
            logger.exception('Error generating thumbnail: %s' % e)
        return self.thumbnail

# cache series properties to speed up loading admin page for series
class SeriesProperties(models.Model):
    series = models.OneToOneField(Series,related_name='properties')
    aantal = models.IntegerField(default = 0)
    min = models.FloatField(default = 0, null = True)
    max = models.FloatField(default = 0, null = True)
    van = models.DateTimeField(null = True)
    tot = models.DateTimeField(null = True)
    gemiddelde = models.FloatField(default = 0, null = True)
    eerste = models.ForeignKey('DataPoint',null = True, related_name='first')
    laatste = models.ForeignKey('DataPoint',null = True, related_name='last')
    beforelast = models.ForeignKey('DataPoint', null = True, related_name='beforelast')  

    def update(self, save = True):
        agg = self.series.datapoints.aggregate(van=Min('date'), tot=Max('date'), min=Min('value'), max=Max('value'), avg=Avg('value'))
        self.aantal = self.series.datapoints.count()
        self.van = agg.get('van', datetime.datetime.now())
        self.tot = agg.get('tot', datetime.datetime.now())
        self.min = agg.get('min', 0)
        self.max = agg.get('max', 0)
        self.gemiddelde = agg.get('avg', 0)
        if self.aantal == 0:
            self.eerste = None
            self.laatste = None
            self.beforelast = None
        else:
            self.eerste = self.series.datapoints.order_by('date')[0]
            if self.aantal == 1:
                self.laaste = self.eerste
                self.beforelast =  self.laatste
            else:
                points = self.series.datapoints.order_by('-date')
                self.laatste = points[0]
                self.beforelast = points[1]
        if save:
            self.save()
            
    
class Variable(models.Model):
    locatie = models.ForeignKey(MeetLocatie)
    name = models.CharField(max_length=10, verbose_name = 'variabele')
    series = models.ForeignKey(Series)
    
    def __unicode__(self):
        return '%s = %s' % (self.name, self.series)

    class Meta:
        verbose_name='variabele'
        verbose_name_plural='variabelen'
        unique_together = ('locatie', 'name', )

# Series that can be edited manually
# class ManualSeries(Series):
#     locatie = models.ForeignKey(MeetLocatie)
#     
#     def meetlocatie(self):
#         return self.locatie
#         
#     def __unicode__(self):
#         return self.name
# 
#     def get_series_data(self,data,start=None):
#         return self.to_pandas(start=start)
#     
#     class Meta:
#         verbose_name = 'Handmatige reeks'
#         verbose_name_plural = 'Handmatige reeksen'
#         
class Formula(Series):
    locatie = models.ForeignKey(MeetLocatie)
    formula_text = models.TextField(blank=True,null=True,verbose_name='berekening')
    formula_variables = models.ManyToManyField(Variable,verbose_name = 'variabelen')
    intersect = models.BooleanField(default=True,verbose_name = 'bereken alleen voor overlappend tijdsinterval')
        
    def meetlocatie(self):
        return self.locatie
        
    def __unicode__(self):
        return self.name

    def get_variables(self):
        variables = {var.name: var.series.to_pandas() for var in self.formula_variables.all()}
        if self.resample is not None and len(self.resample)>0:
            for name,series in variables.iteritems():
                variables[name] = series.resample(rule=self.resample, how=self.aggregate)
        
        # add all series into a single dataframe 
        df = pd.DataFrame(variables)

        if self.intersect:
            # using intersecting time interval only (no extrapolation)
            start = max([v.index.min() for v in variables.values()])
            stop = min([v.index.max() for v in variables.values()])
            df = df[start:stop]

        # interpolate missing values
        df = df.interpolate(method='time')
        
        # return dataframe as dict
        return df.to_dict('series')

    def get_series_data(self,data,start=None):
        variables = self.get_variables()
        result = eval(self.formula_text, globals(), variables)
        if isinstance(result, pd.DataFrame):
            result = result[0]
        if isinstance(result, pd.Series):
            result.name = self.name
        return self.do_postprocess(result)
    
    def get_dependencies(self):
        ''' return list of dependencies in order of processing '''
        deps = []
        for v in self.formula_variables.all():
            s = v.series
            try:
                f = s.formula
                deps.extend(f.get_dependencies())
            except Formula.DoesNotExist:
                pass
            deps.append(s)
        return deps
    
    class Meta:
        verbose_name = 'Berekende reeks'
        verbose_name_plural = 'Berekende reeksen'
    
class DataPoint(models.Model):
    series = models.ForeignKey(Series,related_name='datapoints')
    date = models.DateTimeField()
    value = models.FloatField()
    
    class Meta:
        unique_together=('series','date')
        #ordering = ['date']
        
    def jdate(self):
        return self.date.date

PERIOD_CHOICES = (
              ('hours', 'uur'),
              ('days', 'dag'),
              ('weeks', 'week'),
              ('months', 'maand'),
              ('years', 'jaar'),
              )

import dateutil
    
class Chart(models.Model):
    name = models.CharField(max_length = 50, verbose_name = 'naam')
    description = models.TextField(blank=True,null=True,verbose_name='toelichting',help_text='Toelichting bij grafiek op het dashboard')
    title = models.CharField(max_length = 50, verbose_name = 'titel')
    user=models.ForeignKey(User,default=User)
    start = models.DateTimeField(blank=True,null=True)
    stop = models.DateTimeField(blank=True,null=True)
    percount = models.IntegerField(default=2,verbose_name='aantal perioden',help_text='maximaal aantal periodes die getoond worden (0 = alle perioden)')
    perunit = models.CharField(max_length=10,choices = PERIOD_CHOICES, default = 'months', verbose_name='periodelengte')

    def tijdreeksen(self):
        return self.series.count()
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('acacia:chart-view', args=[self.id])

    def auto_start(self):
        if self.start is None:
            tz = timezone.get_current_timezone()
            start = timezone.make_aware(datetime.datetime.now(),tz)
            for cs in self.series.all():
                t0 = cs.t0
                if t0 is None:
                    t0 = cs.series.van()
                if t0 is not None:
                    start = min(t0,start)
            if self.percount > 0:
                kwargs = {self.perunit: -self.percount}
                delta = dateutil.relativedelta.relativedelta(**kwargs)
                pstart = timezone.make_aware(datetime.datetime.now() + delta, tz)
                if start is None:
                    return pstart
                start = max(start,pstart) 
            return start
        return self.start

    def to_pandas(self):
        s = { cd.series.name: cd.series.to_pandas() for cd in self.series.all() }
        return pd.DataFrame(s)
    
    def to_csv(self):
        io = StringIO.StringIO()
        df = self.to_pandas()
        df.to_csv(io,index_label='Datum/tijd')
        return io.getvalue()
        
    class Meta:
        ordering = ['name',]
        verbose_name = 'Grafiek'
        verbose_name_plural = 'Grafieken'

        
AXIS_CHOICES = (
                ('l', 'links'),
                ('r', 'rechts'),
               )

class ChartSeries(models.Model):
    chart = models.ForeignKey(Chart,related_name='series', verbose_name='grafiek')
    order = models.IntegerField(default=1,verbose_name='volgorde')
    series = models.ForeignKey(Series, verbose_name = 'tijdreeks')
    name = models.CharField(max_length=50,blank=True,null=True,verbose_name='legendanaam')
    axis = models.IntegerField(default=1,verbose_name='Nummer y-as')
    axislr = models.CharField(max_length=2, choices=AXIS_CHOICES, default='l',verbose_name='Positie y-as')
    color = models.CharField(null=True,blank=True,max_length=20, verbose_name = 'Kleur', help_text='Standaard kleur (bv Orange) of rgba waarde (bv rgba(128,128,0,1)) of hexadecimaal getal (bv #ffa500)')
    type = models.CharField(max_length=10, default='line', choices = SERIES_CHOICES)
    stack = models.CharField(max_length=20, blank=True, null=True, verbose_name = 'stapel', help_text='leeg laten of <i>normal</i> of <i>percent</i>')
    label = models.CharField(max_length=20, blank=True,null=True,default='',help_text='label op de y-as')
    y0 = models.FloatField(null=True,blank=True,verbose_name='ymin')
    y1 = models.FloatField(null=True,blank=True,verbose_name='ymax')
    t0 = models.DateTimeField(null=True,blank=True,verbose_name='start')
    t1 = models.DateTimeField(null=True,blank=True,verbose_name='stop')
    
    def __unicode__(self):
        return self.series
    
    def theme(self):
        s = self.series
        return None if s is None else s.theme

    class Meta:
        ordering = ['order', 'name',]
        verbose_name = 'tijdreeks'
        verbose_name_plural = 'tijdreeksen'

from django.template.loader import render_to_string

class Dashboard(models.Model):
    name = models.CharField(max_length=50, verbose_name= 'naam')
    description = models.TextField(blank=True, null=True,verbose_name = 'omschrijving')
    charts = models.ManyToManyField(Chart, verbose_name = 'grafieken', through='DashboardChart')
    user=models.ForeignKey(User,default=User)
    
    def grafieken(self):
        return self.charts.count()

    def sorted_charts(self):
        return self.charts.order_by('dashboardchart__order')
    
    def get_absolute_url(self):
        return reverse('acacia:dash-view', args=[self.id]) 

    def __unicode__(self):
        return self.name
    
#     def summary(self):
#         '''summary as html for inserting in dashboard'''
#         summary = {'Geinfiltreerd': {'Debiet': "23 m3", 'EC': "788 uS/cm"}, 'Onttrokken': {'Debiet': "14 m3", 'EC': "800 uS/cm"} }
#         return render_to_string('data/dash-summary.html', {'summary': summary})

    class Meta:
        ordering = ['name',]

class DashboardChart(models.Model):
    chart = models.ForeignKey(Chart, verbose_name='Grafiek')
    dashboard = models.ForeignKey(Dashboard)
    order = models.IntegerField(default = 1, verbose_name = 'volgorde')

    class Meta:
        ordering = ['order',]
        verbose_name = 'Grafiek'
        verbose_name_plural = 'Grafieken'
    
class TabGroup(models.Model):
    location = models.ForeignKey(ProjectLocatie,verbose_name='projectlocatie')
    name = models.CharField(max_length = 40, verbose_name='naam', help_text='naam van dashboard tabgroep')

    def pagecount(self):
        return self.tabpage_set.count()
    pagecount.short_description = 'aantal tabs'
    
    def pages(self):
        return self.tabpage_set.order_by('order')
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('acacia:tabgroup', args=[self.id]) 
    
class TabPage(models.Model):
    tabgroup = models.ForeignKey(TabGroup)
    name = models.CharField(max_length=40,default='basis',verbose_name='naam', help_text='naam van tabpage')
    order = models.IntegerField(default=1,verbose_name='volgorde', help_text='volgorde van tabpage')
    dashboard = models.ForeignKey(Dashboard)

    def __unicode__(self):
        return self.name

# 
# class EmailLog(models.Model):
#     user = models.ForeignKey(User)
#     level = models.CharField(max_length=10, choices = LOGGING_CHOICES, default = 'INFO')
#     datasource = models.ForeignKey(Datasource)
