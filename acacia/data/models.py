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
from django.conf import settings
import upload as up
import numpy as np
import pandas as pd
import json,util,StringIO,pytz,logging
import dateutil
from django.db.models.aggregates import StdDev
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import get_current_timezone, is_naive

THEME_CHOICES = ((None,'standaard'),
                 ('dark-blue','blauw'),
                 ('dark-green','groen'),
                 ('gray','grijs'),
                 ('grid','grid'),
                 ('skies','wolken'),)

def aware(d,tz=None):
    ''' utility function to ensure datetime object has requested timezone '''
    if d is not None:
        if isinstance(d, (datetime.datetime, datetime.date,)):
            if tz is None or tz == '':
                tz = settings.TIME_ZONE
            if not isinstance(tz, timezone.tzinfo):
                tz = pytz.timezone(tz)
            try:
                if timezone.is_naive(d):
                    return timezone.make_aware(d, tz)            
            except Exception as e:
#                 pytz.NonExistentTimeError, pytz.AmbiguousTimeError: # CET/CEST transition?
                try:
                    return timezone.make_aware(d, pytz.utc)
                except:
                    pass
            else:
                return d.astimezone(tz)
    return d

from django.utils.deconstruct import deconstructible

@deconstructible
class LoggerSourceMixin(object):
    ''' Mixin that provides a logging adapter that adds source context to log records
    Used to send emails to users that follow a source ''' 
    def getLoggerSource(self):
        return self

    def getLogger(self,name=__name__): 
        logger = logging.getLogger(name)  
        return logging.LoggerAdapter(logger,extra={'source': self.getLoggerSource()})

class Project(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True,null=True,verbose_name='omschrijving')
    image = models.ImageField(upload_to=up.project_upload, blank = True, null=True)
    logo = models.ImageField(upload_to=up.project_upload, blank=True, null=True)
    theme = models.CharField(max_length=50,null=True, blank=True,verbose_name='thema', default='dark-blue',choices=THEME_CHOICES,help_text='Thema voor grafieken')
        
    def series(self):
        s = []
        for m in self.projectlocatie_set.all():
            s.extend(m.series())
        return s

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
    name = models.CharField(max_length=100,verbose_name='naam')
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
    name = models.CharField(max_length=100,verbose_name='naam')
    description = models.TextField(blank=True,null=True,verbose_name='omschrijving')
    image = models.ImageField(upload_to=up.meetlocatie_upload, blank = True, null = True)
    location = geo.PointField(dim=2,srid=util.RDNEW,verbose_name='locatie', help_text='Meetlocatie in Rijksdriehoekstelsel coordinaten')
    objects = geo.GeoManager()
    webcam = models.ForeignKey(Webcam, null = True, blank=True)

    def project(self):
        return self.projectlocatie.project
        
    def latlon(self):
        return util.toWGS84(self.location)

    def datasourcecount(self):
        return self.datasource_set.count()
    datasourcecount.short_description = 'Aantal datasources'

    def get_absolute_url(self):
        return reverse('acacia:meetlocatie-detail',args=[self.id])
    
    def __unicode__(self):
        try:
            return '%s %s' % (self.projectlocatie, self.name)
        except ProjectLocatie.DoesNotExist:
            return self.name

    class Meta:
        ordering = ['name',]
        unique_together = ('projectlocatie', 'name')

    def filecount(self):
        return sum([d.filecount() or 0 for d in self.datasources.all()])

    def paramcount(self):
        return sum([d.parametercount() or 0 for d in self.datasources.all()])

    def series(self):
        return self.series_set.all()
        
    def getseries(self):
        return self.series()
    
    def charts(self):
        charts = []
        for s in self.series():
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
    url = models.URLField(blank=True,null=True,verbose_name = 'Default url')
    
    def get_class(self):
        return classForName(self.classname)
    
    def __unicode__(self):
        return self.name
        
    class Meta:
        ordering = ['name',]

LOGGING_CHOICES = (
                  ('DEBUG', 'Debug'),
                  ('INFO', 'Informatie'),
                  ('WARNING', 'Waarschuwingen'),
                  ('ERROR', 'Fouten'),
#                  ('CRITICAL', 'Alleen kritieke fouten'),
                  )

def timezone_choices():
    return [(tz,tz) for tz in pytz.all_timezones]

TIMEZONE_CHOICES = timezone_choices()

class Datasource(models.Model, LoggerSourceMixin):
    name = models.CharField(max_length=100,verbose_name='naam')
    description = models.TextField(blank=True,null=True,verbose_name='omschrijving')
    meetlocatie=models.ForeignKey(MeetLocatie,null=True,blank=True,verbose_name='Primaire meetlocatie',help_text='Primaire meetlocatie van deze gegevensbron')
    locations=models.ManyToManyField(MeetLocatie,blank=True,related_name='datasources',verbose_name='locaties', help_text='Secundaire meetlocaties die deze gegevensbron gebruiken')
    url=models.CharField(blank=True,null=True,max_length=200,help_text='volledige url van de gegevensbron. Leeg laten voor handmatige uploads of default url van generator')
    generator=models.ForeignKey(Generator,help_text='Generator voor het maken van tijdreeksen uit de datafiles')
    user=models.ForeignKey(User,verbose_name='Aangemaakt door')
    created = models.DateTimeField(auto_now_add=True,verbose_name='Aangemaakt op')
    last_download = models.DateTimeField(null=True, blank=True, verbose_name='geactualiseerd')
    autoupdate = models.BooleanField(default=True)
    config=models.TextField(blank=True,null=True,default='{}',verbose_name = 'Additionele configuraties',help_text='Geldige JSON dictionary')
    username=models.CharField(max_length=50, blank=True, null=True, default='anonymous', verbose_name='Gebuikersnaam',help_text='Gebruikersnaam voor downloads')
    password=models.CharField(max_length=50, blank=True, null=True, verbose_name='Wachtwoord',help_text='Wachtwoord voor downloads')
    timezone=models.CharField(max_length=50, blank=True, verbose_name = 'Tijdzone', default=settings.TIME_ZONE,choices=TIMEZONE_CHOICES)

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

    def get_generator_instance(self,**kwargs):
        logger = self.getLogger()
        if self.generator is None:
            raise Exception('Generator not defined for datasource %s' % self.name)
        gen = self.generator.get_class()
        if self.config:
            try:
                kwargs.update(json.loads(self.config))
            except Exception as err:
                logger.error('Configuration error in generator %s: %s' % (self.generator, err))
                return None
        return gen(**kwargs)
    
    def build_download_options(self,start=None):
        logger = self.getLogger()
        options = {}
        
        if self.meetlocatie:
            #lonlat = self.meetlocatie.latlon() # does not initialize geo object manager
            loc = MeetLocatie.objects.get(pk=self.meetlocatie.pk)
            lonlat = loc.latlon()
            options['lonlat'] = (lonlat.x,lonlat.y)
            options['meetlocatie'] = unicode(loc)
        if self.username:
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

        url = self.url or self.generator.url
        if not url:
            logger.error('Cannot download datasource %s: no default url available' % (self.name))
            return None

        options['url']=url

        return options
                   
    def download(self, start=None):
        logger = self.getLogger()
        if self.generator is None:
            logger.error('Cannot download datasource %s: no generator defined' % (self.name))
            return None

        gen = self.get_generator_instance()
        if gen is None:
            logger.error('Cannot download datasource %s: could not create instance of generator %s' % (self.name, self.generator))
            return None

        options = self.build_download_options(start)
        if options is None:
            return None
        
        logger.info('Downloading datasource %s from %s' % (self.name, options['url']))
        try:
            
            files = []
            crcs = {f.crc:f.file for f in self.sourcefiles.all()}

            def callback(result):
                for filename, contents in result.iteritems():
                    crc = abs(binascii.crc32(contents))
                    if crc in crcs:
                        logger.warning('Downloaded file %s ignored: identical to local file %s' % (filename, crcs[crc].file.name))
                        continue
                    try:
                        sourcefile = self.sourcefiles.get(name=filename)
                    except:
                        sourcefile = SourceFile(name=filename,datasource=self,user=self.user)
                    sourcefile.crc = crc
                    contentfile = ContentFile(contents)
                    try:
                        sourcefile.file.save(name=filename, content=contentfile)
                        logger.debug('File %s saved to %s' % (filename, sourcefile.filepath()))
                        crcs[crc] = sourcefile.file
                        files.append(sourcefile)
                    except Exception as e:
                        logger.exception('Problem saving file %s: %s' % (filename,e))

            options['callback'] = callback
            results = gen.download(**options)

        except Exception as e:
            logger.exception('Error downloading datasource %s: %s' % (self.name, e))
            return None            
        logger.info('Download completed, got %s file(s)', len(results))
        self.last_download = aware(timezone.now(),self.timezone)
        self.save(update_fields=['last_download'])
        return files
        
    def update_parameters(self,data=None,files=None,limit=0):
        logger = self.getLogger()
        gen = self.get_generator_instance()
        if gen is None:
            return
        logger.debug('Updating parameters for datasource %s' % self.name)
        params = {}
        if files is None:
            files = self.sourcefiles.all();
            if limit != 0:
                limit = abs(limit)
                # take only last few entries
                files = list(files);
                if len(files) > limit:
                    files = files[-limit];
        for sourcefile in files:
            try:
                try:
                    params.update(gen.get_parameters(sourcefile.file))
                    sourcefile.file.close()
                except Exception as e:
                    logger.exception('Cannot update parameters for sourcefile %s: %s' % (sourcefile, e))
            except Exception as e:
                logger.exception('Cannot open sourcefile %s: %s' % (sourcefile, e))
        logger.debug('Update completed, got %d parameters from %d files', len(params),len(files))
        num_created = 0
        num_updated = 0
        for name,defaults in params.iteritems():
            name = name.strip()
            if name == '':
                continue
            try:
                param = self.parameter_set.get(name=name)
                num_updated = num_updated+1
            except Parameter.DoesNotExist:
                logger.info('parameter %s created' % name)
                param = Parameter(name=name,**defaults)
                param.datasource = self
                num_created = num_created+1
            param.save()
        logger.debug('%d parameters created, %d updated' % (num_created, num_updated))
        return num_created+num_updated

    def replace_parameters(self,data=None):
        self.parameter_set.all().delete()
        self.update_parameters(data)

    def make_thumbnails(self, data=None):
        if data is None:
            data = self.get_data()
        for p in self.parameter_set.all():
            p.make_thumbnail(data)
    
    def get_data(self,**kwargs):
        logger = self.getLogger()
        gen = self.get_generator_instance(**kwargs)
        logger.debug('Getting data for datasource %s', self.name)
        datadict = {}
        start = aware(kwargs.get('start', None))
        stop = aware(kwargs.get('stop', None))
        files = kwargs.get('files', None)
        if files is None:
            files = self.sourcefiles.all()

        for sourcefile in files:

            if start is not None:
                sstop = aware(sourcefile.stop,self.timezone)
                if sstop is not None and sstop < start:
                    continue
            if stop is not None:
                sstart = aware(sourcefile.start,self.timezone)
                if sstart is not None and sstart > stop:
                    continue
                
            # retrieve dict of loc, dataframe for location(s) in sourcefile
            d = sourcefile.get_data(gen,**kwargs)
            if d:
                for loc, data in d.iteritems():

                    if not loc in datadict:
                        datadict[loc] = data
                    else:
                        datadict[loc] = datadict[loc].append(data)
                        
        for loc, data in datadict.iteritems():
            # sourcefile.get_data has already set the timezone, code below is redundant?
            timezone = pytz.timezone(self.timezone)
            date = np.array([aware(d, timezone) for d in data.index.to_pydatetime()])
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
            if self.calibrationdata_set:
                data = self.calibrate(data)
            datadict[loc] = data.sort_index()
        return datadict

    def get_locations(self,**kwargs):
        logger = self.getLogger()
        logger.debug('Getting locations for datasource %s', self.name)
        files = kwargs.get('files', None) or self.sourcefiles.all()
        locs = {}
        for sourcefile in files:
            locs.update(sourcefile.get_locations())
        return locs
    
    def calibrate_value(self, value, sensor, calib):
        ''' return calibrated sensor data 
            sensor is iterable with sorted sensor values            
            calib is iterable with corresponding calibration values            
        '''
        n = len(sensor) # number of calibration points
        for i,d in enumerate(sensor):
            if value < d:
                break
        i = max(1,min(i,n-1))
        s1 = sensor[i-1]
        s2 = sensor[i]
        ds = s2-s1
        c1 = calib[i-1]
        c2 = calib[i]
        dc = c2-c1
        if value < s1 or value > s2:
            return None
        calval = c1 + (value - s1) * (dc / ds) 
        return calval
    
    def calibrate(self,data):
        for name in data.columns:
            try:
                par = self.parameter_set.get(name=name)
            except:
                # no such parameter
                continue
            caldata = self.calibrationdata_set.filter(parameter=par).order_by('sensor_value')
            if caldata:
                caldata = [(d.sensor_value, d.calib_value) for d in caldata]
                x,y = zip(*caldata)
                sensdata = data[name]
                data[name] = [self.calibrate_value(value,x,y) for value in sensdata]
        return data
                
    def to_csv(self):
        io = StringIO.StringIO()
        df = self.get_data()
        if df is None:
            return None
        num = len(df)
        for loc, frame in df.items():
            if num > 1:
                # add name of location to dataframe
                frame['location'] = unicode(loc)
            frame.to_csv(io, index_label='Datum/tijd')
        return io.getvalue()

    def parametercount(self):
        count = self.parameter_set.count()
        return count if count>0 else None
    parametercount.short_description = 'parameters'

    def locationcount(self):
        count = self.locations.count()
        return count if count>0 else None
    locationcount.short_description = 'locaties'

    def filecount(self):
        count = self.sourcefiles.count()
        return count if count>0 else None
    filecount.short_description = 'files'

    def calibcount(self):
        count = self.calibrationdata_set.count()
        return count if count>0 else None
    calibcount.short_description = 'IJkpunten'

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
    # TODO: ook meetlocatie of projectlocatie volgen (ivm berekende reeksen)
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
    
    def meetlocatie(self):
        return self.datasource.meetlocatie
    
# class UpdateSchedule(models.Model):
#     datasource = models.ForeignKey(Datasource)
#     minute = models.CharField(max_length=2,default='0')
#     hour = models.CharField(max_length=2,default='0')
#     day = models.CharField(max_length=2,default='*')
#     month = models.CharField(max_length=2,default='*')
#     dayofweek = models.CharField(max_length=1,default='*')
#     active = models.BooleanField(default=True)
    
class SourceFile(models.Model,LoggerSourceMixin):
    name=models.CharField(max_length=100,blank=True)
    datasource = models.ForeignKey('Datasource',related_name='sourcefiles', verbose_name = 'gegevensbron')
    file=models.FileField(max_length=200,upload_to=up.sourcefile_upload,blank=True,null=True)
    rows=models.IntegerField(default=0,verbose_name='rijen')
    cols=models.IntegerField(default=0,verbose_name='kolommen')
    locs=models.IntegerField(default=0,verbose_name='locaties')
    start=models.DateTimeField(null=True,blank=True)
    stop=models.DateTimeField(null=True,blank=True)
    crc=models.IntegerField(default=0)
    user=models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True,verbose_name='aangemaakt')
    uploaded = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name
     
    class Meta:
#        unique_together = ('name', 'datasource',)
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
            date = aware(date,self.datasource.timezone or get_current_timezone())
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
    filepath.short_description = 'bestandslocatie'

    def filetag(self):
        return '<a href="%s">%s</a>' % (os.path.join(settings.MEDIA_URL,self.file.name),self.filename())
    filetag.allow_tags=True
    filetag.short_description='bestand'

    def get_data_dimensions(self, data):
        tz = self.datasource.timezone or get_current_timezone()
        numrows=0
        cols=set()
        begin=None
        end=None
        for k,v in data.iteritems():
            rows = v.shape[0]
            if rows:
                numrows += rows
                start = aware(min(v.index), tz)
                begin = min(begin,start) if begin else start 
                stop = aware(max(v.index), tz)
                end = max(end,stop) if end else stop 
                for colname in v.columns.values:
                    cols.add(colname)
        numcols=len(cols)
        numlocs = len(data)
        
        self.cols = numcols
        self.rows = numrows
        self.locs = numlocs
        self.start= begin
        self.stop = end
        
        return (numlocs,numrows,numcols,begin,end)
    
    def get_data(self,gen=None,**kwargs):
        logger = self.getLogger()
        data = None
        if gen is None:
            gen = self.datasource.get_generator_instance(**kwargs)
        try:
            filename = self.file.name
        except:
            logger.error('Sourcefile %s has no associated file' % self.name)
            return None
        logger.debug('Getting data for sourcefile %s', self.name)
        closed = self.file.closed
        try:
            if closed:
                self.file.open()
            data = gen.get_data(self.file,**kwargs)
        except Exception as e:
            logger.exception('Error retrieving data from %s: %s' % (filename, e))
            return None
        finally:
            if closed:
                self.file.close()

        if data is None:
            logger.warning('No data retrieved from %s' % filename)
        else:
            # generator may return single dataframe or dict with location as key
            if isinstance(data,pd.DataFrame):
                if data.empty:
                    logger.warning('No data retrieved from %s' % filename)
                loc = kwargs.get('meetlocatie',self.meetlocatie())
                data={loc:data}
            self.get_data_dimensions(data)
            logger.debug('Got %d locations, %d rows, %d columns', self.locs,self.rows,self.cols)

        # set timezone of data
        # data should have a datetimeindex
        tz = self.datasource.timezone or get_current_timezone()
        for k,v in data.items():
            if hasattr(v.index,'tz') and v.index.tz:
                data[k]=v.tz_convert(tz)
            else:
                try:
                    data[k]=v.tz_localize(tz,ambiguous='infer')
                except Exception as ex:
                    data[k]=v.tz_localize(tz,ambiguous='NaT')
        return data

    def get_locations(self,gen=None):
        logger=self.getLogger()
        if gen is None:
            gen = self.datasource.get_generator_instance()
        try:
            filename = self.file.name
        except:
            logger.error('Sourcefile %s has no associated file' % self.name)
            return None
        logger.debug('Getting locations for sourcefile %s', self.name)
        try:
            locs = gen.get_locations(self.file)
        except Exception as e:
            logger.exception('Error retrieving locations from %s: %s' % (filename, e))
            return None
        if not locs:
            logger.warning('No locations found in %s' % filename)
        else:
            logger.debug('Got %d locations', len(locs))
        return locs
        
    def get_dimensions(self, data=None):
        if data is None:
            data = self.get_data()
            if data is None:
                self.rows = 0
                self.cols = 0
                self.locs = 0
                self.start = None
                self.stop = None
            else:
                self.get_data_dimensions(data)
            
from django.db.models.signals import pre_delete, pre_save, post_save
from django.dispatch.dispatcher import receiver
from functools import wraps

def loaddata(signal_handler):
    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if kwargs.get('raw', False):
            #called from manage.py loaddata
            print "Skipping signal for %s %s" % (args, kwargs)
            return
        signal_handler(*args, **kwargs)
    return wrapper

@receiver(pre_delete, sender=SourceFile)
@loaddata
def sourcefile_delete(sender, instance, **kwargs):
    logger = instance.getLogger()
    filename = instance.file.name
    logger.debug('Deleting file %s for datafile %s' % (filename, instance.name))
    instance.file.delete(False)
    logger.debug('File %s deleted' % filename)

@receiver(pre_save, sender=SourceFile)
@loaddata
def sourcefile_save(sender, instance, **kwargs):
    logger = instance.getLogger()
    date = instance.filedate()
    if date:
        if instance.uploaded is None or date > instance.uploaded:
            instance.uploaded = date
    try:
        instance.get_dimensions(data = kwargs.get('data', None))
    except Exception as e:
        logger.exception('Error getting dimensions while saving sourcefile %s: %s' % (instance, e))
    ds = instance.datasource
    if instance.uploaded is None:
        instance.uploaded = aware(timezone.now(),instance.datasource.timezone or get_current_timezone())
    if ds.last_download is None:
        ds.last_download = instance.uploaded
    elif ds.last_download < instance.uploaded:
        ds.last_download = instance.uploaded
    ds.save()

SERIES_CHOICES = (('line', 'lijn'),
                  ('column', 'staaf'),
                  ('scatter', 'punt'),
                  ('area', 'area'),
                  ('spline', 'spline')
                  )
        
class Parameter(models.Model, LoggerSourceMixin):
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
        return self.datasource.get_data(parameter=self.name,**kwargs)

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
        logger = self.getLogger()
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
            logger.debug('Generated thumbnail %s' % dest)
            self.save()
        except Exception as e:
            logger.exception('Error generating thumbnail for parameter %s: %s' % (self.name, e))
            return None
        return self.thumbnail
    
@receiver(pre_delete, sender=Parameter)
@loaddata
def parameter_delete(sender, instance, **kwargs):
    logger=instance.getLogger()
    logger.debug('Deleting thumbnail %s for parameter %s' % (instance.thumbnail.name, instance.name))
    instance.thumbnail.delete(False)
    logger.debug('Thumbnail deleted')

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

from polymorphic.manager import PolymorphicManager
from polymorphic.models import PolymorphicModel

class Series(PolymorphicModel,LoggerSourceMixin):
    mlocatie = models.ForeignKey(MeetLocatie,null=True,blank=True,verbose_name='meetlocatie')
    name = models.CharField(max_length=100,verbose_name='naam')
    description = models.TextField(blank=True,null=True,verbose_name='omschrijving')
    unit = models.CharField(max_length=10, blank=True, null=True, verbose_name='eenheid')
    type = models.CharField(max_length=20, blank = True, verbose_name='weergave', help_text='Standaard weeggave op grafieken', default='line', choices = SERIES_CHOICES)
    parameter = models.ForeignKey(Parameter, null=True, blank=True)
    thumbnail = models.ImageField(upload_to=up.series_thumb_upload, max_length=200, blank=True, null=True)
    user=models.ForeignKey(User)
    objects = PolymorphicManager()
    timezone = models.CharField(max_length=20,blank=True,choices=TIMEZONE_CHOICES,verbose_name='tijdzone')

    # tijdsinterval
    limit_time = models.BooleanField(default = False,verbose_name='tijdsrestrictie',help_text='Beperk tijdreeks tot gegeven tijdsinterval')
    from_limit = models.DateTimeField(blank=True,null=True,verbose_name='Begintijd')
    to_limit = models.DateTimeField(blank=True,null=True,verbose_name='Eindtijd')
    
    # Nabewerkingen
    resample = models.CharField(max_length=10,choices=RESAMPLE_METHOD,blank=True, null=True, 
                                verbose_name='frequentie',help_text='Frequentie voor resampling van tijdreeks')
    aggregate = models.CharField(max_length=10,choices=AGGREGATION_METHOD,blank=True, null=True, 
                                 verbose_name='aggregatie', help_text = 'Aggregatiemethode bij resampling van tijdreeks')
    scale = models.FloatField(default = 1.0,verbose_name = 'verschalingsfactor', help_text = 'constante factor voor verschaling van de meetwaarden (vóór compensatie)')
    scale_series = models.ForeignKey('Series',null=True,blank=True,verbose_name='verschalingsreeks', related_name='scaling_set', help_text='tijdreeks voor verschaling van de meetwaarden (vóór compensatie')

    offset = models.FloatField(default = 0.0, verbose_name = 'compensatieconstante', help_text = 'constante voor compensatie van de meetwaarden (ná verschaling)')
    offset_series = models.ForeignKey('Series',null=True, blank=True, verbose_name='compensatiereeks',related_name='offset_set', help_text = 'tijdreeks voor compensatie van de meetwaarden (ná verschaling)' )
    
    cumsum = models.BooleanField(default = False, verbose_name='accumuleren', help_text = 'reeks transformeren naar accumulatie')
    cumstart = models.DateTimeField(blank = True, null = True, verbose_name='start accumulatie')
    
    class Meta:
        ordering = ['name',]
        unique_together = ('parameter','name','mlocatie')
        verbose_name = 'Tijdreeks'
        verbose_name_plural = 'Tijdreeksen'
        
    def get_absolute_url(self):
        return reverse('acacia:series-detail', args=[self.id]) 
    
    def typename(self):
        from django.contrib.contenttypes.models import ContentType
        return ContentType.objects.get_for_id(self.polymorphic_ctype_id).name
    typename.short_description = 'reekstype'
    
    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "name__icontains",)
    
    def datasource(self):
        try:
            p = self.parameter
        except:
            # Parameter defined but does not exist. Database integrity problem!
            return None
        return None if p is None else p.datasource

    def meetlocatie(self):
        if not self.mlocatie:
            self.set_locatie()
        return self.mlocatie

    def set_locatie(self):
        d = self.datasource()
        self.mlocatie = None if d is None else d.meetlocatie
        
    def projectlocatie(self):
        l = self.meetlocatie()
        return None if l is None else l.projectlocatie

    def project(self):
        p = self.projectlocatie()
        return None if p is None else p.project

    def theme(self):
        p = self.project()
        return None if p is None or p.theme is None else 'themes/%s.js' % p.theme
    
    def default_type(self):
        p = self.parameter
        return 'line' if p is None else p.type

    def default_timezone(self):
        ds = self.datasource()
        if ds:
            return ds.timezone or get_current_timezone()
        else:
            return get_current_timezone()

    def __unicode__(self):
        ds = self.datasource()
        if ds:
            src = ds.name
        else:
            ml = self.meetlocatie()
            if ml:
                src  = ml.name
            else:
                src = '(berekend)'
        return '%s - %s' % (src, self.name)
    
    def do_align(self, s1, s2):
        ''' align series s2 with s1 and fill missing values by padding'''
        # align series and forward fill the missing data
        if is_naive(s1.index):
            if not is_naive(s2.index):
                s1 = s1.tz_localize(s2.index.tz,ambiguous='infer')
        elif is_naive(s2.index):
            s2 = s2.tz_localize(s1.index.tz,ambiguous='infer')
        else: 
            s1 = s1.tz_convert(s2.index.tz)
        a,b = s1.align(s2,method='pad')
        # back fill na values (in case s2 starts after s1)
        s2 = b.fillna(method='bfill')
        return (s1,s2)
    
    def do_offset(self, s1, s2):
        ''' apply offset to series '''
        s1,s2 = self.do_align(s1, s2)
        return s1 + s2

    def do_scale(self, s1, s2):
        ''' scale series s1 with s2 '''
        s1,s2 = self.do_align(s1, s2)
        return s1 * s2
    
    def do_postprocess(self, series, start=None, stop=None):
        ''' perform postprocessing of series data like resampling, scaling etc'''

        logger = self.getLogger()

        # remove n/a values
        series = series.dropna()
        if series.empty:
            return series
 
        # remove duplicates and sort on time
        series = series.groupby(series.index).last().sort_index()
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
                begin = pd.to_datetime(series.index[0]) #begin nieuwe reeks
                try:
                    before = self.datapoints.filter(date__lt = begin).order_by('-date')
                    if before:
                        add_value = before[0].value
                except Exception as e:
                    logger.exception('Accumulation of series %s failed: %s' % (self.name, e))

        # apply scaling
        if self.scale != 1.0:
            series = series * self.scale
        if self.scale_series is not None:
            series = self.do_scale(series, self.scale_series.to_pandas())

        #  apply offset
        if add_value != 0:
            # this is a cumulative series with a partial interval
            # add sum from previous interval instead of series.offset
            series = series + add_value
        else:
            if self.offset != 0.0:
                series = series + self.offset
            if self.offset_series is not None:
                series = self.do_offset(series, self.offset_series.to_pandas())

        # clip on time
        if start is None:
            start = self.from_limit
        if stop is None:
            stop = self.to_limit
        if start is None and stop is None:
            return series
        elif start is None:
            return series[:stop]
        elif stop is None:
            return series[start:]
        else:
            return series[start:stop]
         
    def get_series_data(self, data, start=None, stop=None):
        logger = self.getLogger()
       
        if self.parameter is None:
            #raise Exception('Parameter is None for series %s' % self.name)
            return None

        start = start or self.from_limit
        stop = stop or self.to_limit

        if data is None:
            data = self.parameter.get_data(start=start,stop=stop,meetlocatie=self.mlocatie)
            if data is None:
                return None
        if isinstance(data,pd.DataFrame):
            dataframe = data
        else:
            # multiple locations
            if not self.mlocatie:
                # use any location
                _location, dataframe = next(data.items())
            elif self.mlocatie in data:
                dataframe = data[self.mlocatie]
            elif self.mlocatie.name in data:
                dataframe = data[self.mlocatie.name]
            elif None in data and len(data) == 1:
                # no location available, use default
                dataframe = data[None]
            else:
                logger.error('series %s: location %s not found' % (self.name, self.mlocatie.name))
                return None
        if not self.parameter.name in dataframe:
            # maybe datasource has stopped reporting about this parameter?
            msg = 'series %s: parameter %s not found' % (self.name, self.parameter.name)
            logger.error(msg)
            return None
        
        series = dataframe[self.parameter.name]
        if isinstance(series,pd.DataFrame):
            # drop duplicate column names, retain first
            series = series.T.ix[0].T
        series = self.do_postprocess(series, start, stop)
        return series
    
    def prepare_points(self, series, tz=None):
        ''' return array of datapoints in given timezone from pandas series'''
        pts = []
        for date,value in series.iteritems():
            try:
                value = float(value)
                if math.isnan(value) or date is None:
                    continue
                pts.append(DataPoint(series=self, date=aware(date,tz), value=value))
            except Exception as e:
                self.getLogger().debug('Datapoint %s,%g: %s' % (str(date), value, e))
        return pts
    
    def create_points(self, series, tz):
        return self.datapoints.bulk_create(self.prepare_points(series, tz))
    
    def create(self, data=None, thumbnail=True):
        logger = self.getLogger()
        logger.debug('Creating series %s' % self.name)
        series = self.get_series_data(data)
        if series is None:
            logger.error('Creation of series %s failed' % self.name)
            return 0
        created = self.create_points(series, self.timezone)
        num_created = len(created)
        logger.info('Series %s updated: %d points created, %d points skipped' % (self.name, num_created, series.count() - num_created))
        if thumbnail and num_created > 0:
            self.make_thumbnail()
        self.save()
        return num_created
    
    def replace(self, data=None):
        logger = self.getLogger()
        logger.debug('Deleting all %d datapoints from series %s' % (self.datapoints.count(), self.name))
        self.datapoints.all().delete()
        return self.create(data)

    def update(self, data=None, start=None, thumbnail=True):
        logger = self.getLogger()

        logger.debug('Updating series %s' % self.name)
        series = self.get_series_data(data, start)
        if series is None:
            logger.error('Update of series %s failed' % self.name)
            return 0
        
        if series.count() == 0:
            logger.warning('No datapoints found in series %s' % self.name)
            return 0;

        # MySQL needs UTC to avoid duplicate index at DST transition 
        pts = self.prepare_points(series,timezone.utc)
        if pts == []:
            logger.warning('No valid datapoints found in series %s' % self.name)
            return 0;
        

        # delete properties first to avoid foreignkey constraint failure
        try:
            self.properties.delete()
        except:
            pass
        # delete the points
        if start is None:
            start = min([p.date for p in pts])
        query = self.datapoints.filter(date__gte=start)
        deleted = query.delete()
        num_deleted = len(deleted) if deleted else 0

        created = self.datapoints.bulk_create(pts)
        num_created = len(created) - num_deleted
        num_updated = num_deleted
        logger.info('Series %s updated: %d points created, %d updated' % (self.name, num_created, num_updated))
        if thumbnail and (num_created > 0 or num_updated > 0):
            self.make_thumbnail()
        self.save()
        return num_created + num_updated
    
    def getproperties(self):
        ''' return properties, creates and updates if no properties exist '''
        try:
            props = self.properties
        except SeriesProperties.DoesNotExist:
            props = SeriesProperties.objects.create(series = self)
            props.update()
        return props

    def update_properties(self):
        ''' return updated properties, creates if no properties exist '''
        try:
            props = self.properties
        except SeriesProperties.DoesNotExist:
            props = SeriesProperties.objects.create(series = self)
        props.update()
        return props
     
    def aantal(self):
        return self.getproperties().aantal
     
    def van(self):
        return self.getproperties().van
 
    def tot(self):
        return self.getproperties().tot
    
    def minimum(self):
        return self.getproperties().min
 
    def maximum(self):
        return self.getproperties().max
 
    def gemiddelde(self):
        return self.getproperties().gemiddelde

    def stddev(self):
        return self.getproperties().stddev
 
    def laatste(self):
        return self.getproperties().laatste
 
    def beforelast(self):
        return self.getproperties().beforelast
         
    def eerste(self):
        return self.getproperties().eerste
         
    def thumbpath(self):
        return self.thumbnail.path
         
    def thumbtag(self):
        return util.thumbtag(self.thumbnail.name)
    
    thumbtag.allow_tags=True
    thumbtag.short_description='thumbnail'

    def filter_points(self, **kwargs):
        start = kwargs.get('start', None)
        stop = kwargs.get('stop', None)

        queryset = self.datapoints.order_by('date')
        raw = kwargs.get('raw', False)
        if self.validated and not raw:
            queryset = self.validation.validpoint_set.order_by('date')
            first = self.validation.invalid_points.first()
            if first:
                queryset = queryset.filter(date__lt=first.date)
                
        if start is None and stop is None:
            return queryset.all()
        if start is None:
            start = self.van()
        if stop is None:
            stop = self.tot()
        return queryset.filter(date__range=[start,stop])
    
    def to_array(self, **kwargs):
        points = self.filter_points(**kwargs)
        return [(dp.date,dp.value) for dp in points]

    def to_pandas(self, **kwargs):
        arr = self.to_array(**kwargs)
        if arr:
            dates,values = zip(*arr)
            return pd.Series(values,index=dates,name=self.name).sort_index()
        else:
            return pd.Series(name=self.name)
            
    def to_csv(self, **kwargs):
        ser = self.to_pandas(**kwargs)
        io = StringIO.StringIO()
        ser.to_csv(io, header=[self.name], index_label='Datum/tijd')
        return io.getvalue()
    
    def make_thumbnail(self):
        logger = self.getLogger()
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
            logger.debug('Generated thumbnail %s' % dest)

        except Exception as e:
            logger.exception('Error generating thumbnail: %s' % e)
        return self.thumbnail

    @property
    def validpoints(self):
        try:
            for v in self.validation.validpoint_set.all():
                if v.value is None:
                    break
                yield v
        except ObjectDoesNotExist:
            # no validation available
            pass
        
    @property
    def is_valid(self):
        try:
            return self.validation.valid 
        except ObjectDoesNotExist:
            # no validation
            return False
    @property
    def validated(self):
        try:
            return self.validation.validated
        except:
            return False
        
    def validate(self,reset=False, accept=False, user=None):
        try:
            val = self.validation
        except:
            # no validation
            return
        if reset:
            val.reset()
        val.persist()
        if accept and user:
            val.accept(user=user)

# cache series properties to speed up loading admin page for series
class SeriesProperties(models.Model):
    series = models.OneToOneField(Series,related_name='properties')
    aantal = models.IntegerField(default = 0)
    min = models.FloatField(default = 0, null = True)
    max = models.FloatField(default = 0, null = True)
    van = models.DateTimeField(null = True)
    tot = models.DateTimeField(null = True)
    gemiddelde = models.FloatField(default = 0, null = True)
    stddev = models.FloatField(default = 0, null = True)
    eerste = models.ForeignKey('DataPoint',null = True, related_name='first')
    laatste = models.ForeignKey('DataPoint',null = True, related_name='last')
    beforelast = models.ForeignKey('DataPoint', null = True, related_name='beforelast')  

    def update(self, save = True):
        agg = self.series.datapoints.aggregate(van=Min('date'), tot=Max('date'), min=Min('value'), max=Max('value'), avg=Avg('value'), std = StdDev('value'))
        self.aantal = self.series.datapoints.count()
        self.van = agg.get('van', datetime.datetime.now())
        self.tot = agg.get('tot', datetime.datetime.now())
        self.min = agg.get('min', 0)
        self.max = agg.get('max', 0)
        self.gemiddelde = agg.get('avg', 0)
        self.stddev = agg.get('std', 0)
        if self.aantal == 0:
            self.eerste = None
            self.laatste = None
            self.beforelast = None
        else:
            self.eerste = self.series.datapoints.order_by('date')[0]
            if self.aantal == 1:
                self.laatste = self.eerste
                self.beforelast = self.eerste
            else:
                points = self.series.datapoints.order_by('-date')
                self.laatste = points[0]
                self.beforelast = points[1]
        if save:
            self.save()

class Variable(models.Model):
    locatie = models.ForeignKey(MeetLocatie)
    name = models.CharField(max_length=20, verbose_name = 'variabele')
    series = models.ForeignKey(Series, verbose_name = 'reeks')

    def thumbtag(self):
        try:
            return self.series.thumbtag()
        except:
            return None
        
    thumbtag.allow_tags = True
    thumbtag.short_description = 'thumbnail'

    def __unicode__(self):
        return '%s = %s' % (self.name, self.series)
        
    class Meta:
        verbose_name='variabele'
        verbose_name_plural='variabelen'
        unique_together = ('locatie', 'name', )

# Series that can be edited manually
class ManualSeries(Series):
    ''' Series that can be edited manually (no datasource, nor parameter)'''
    def __unicode__(self):
        return self.name
 
    def get_series_data(self,data,start=None):
        return self.to_pandas(start=start)
     
    class Meta:
        verbose_name = 'Handmatige reeks'
        verbose_name_plural = 'Handmatige reeksen'
         
class Formula(Series):
    ''' Calculated series '''
    formula_text = models.TextField(blank=True,null=True,verbose_name='berekening')
    formula_variables = models.ManyToManyField(Variable,verbose_name = 'variabelen')
    intersect = models.BooleanField(default=True,verbose_name = 'bereken alleen voor overlappend tijdsinterval')
        
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
            try:
                # sometimes strange errors occur:
                # cannot do slice indexing on <class 'pandas.indexes.range.RangeIndex'> with these indexers [2014-02-20 00:00:00+00:00] of <class 'pandas.tslib.Timestamp'>
                df = df[start:stop]
            except:
                pass

        # interpolate missing values
        df = df.interpolate(method='time')
        
        # return dataframe as dict
        return df.to_dict('series')

    def get_series_data(self,data,start=None,stop=None):
        variables = self.get_variables()
        result = eval(self.formula_text, globals(), variables)
        if isinstance(result, pd.DataFrame):
            result = result[0]
        if isinstance(result, pd.Series):
            result.name = self.name
        return self.do_postprocess(result.tz_convert(self.timezone),None,None)
    
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

@receiver(pre_save, sender=Series)
@receiver(pre_save, sender=ManualSeries)
@receiver(pre_save, sender=Formula)
@loaddata
def series_pre_save(sender, instance, **kwargs):
    if not instance.mlocatie:
        # for parameter series only, others should have mlocatie set
        instance.set_locatie()
    if not instance.timezone:
        instance.timezone = instance.default_timezone()
        
@receiver(post_save, sender=Series)
@receiver(post_save, sender=ManualSeries)
@receiver(post_save, sender=Formula)
@loaddata
def series_post_save(sender, instance, **kwargs):
    try:
        # update (or create) properties should be in post save, because foreignkey to series needs to be valid
        props = instance.getproperties()
        props.update()
    except Exception as e:
        logger = instance.getLogger()
        logger.exception('Error updating properties of %s: %s' % (instance, e))
    
class DataPoint(models.Model):
    id = models.BigAutoField(primary_key=True, unique = True)
    series = models.ForeignKey(Series,related_name='datapoints')
    date = models.DateTimeField(verbose_name='Tijdstip')
    value = models.FloatField(verbose_name='Waarde')
    
    class Meta:
        verbose_name = 'Meetwaarde'
        verbose_name_plural = 'Meetwaarden'
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

   
#class Chart(models.Model):
class Chart(PolymorphicModel):
    name = models.CharField(max_length = 100, verbose_name = 'naam')
    description = models.TextField(blank=True,null=True,verbose_name='toelichting',help_text='Toelichting bij grafiek op het dashboard')
    title = models.CharField(max_length = 100, verbose_name = 'titel')
    user=models.ForeignKey(User)
    start = models.DateTimeField(blank=True,null=True)
    #start_today = models.BooleanField(default=False,verbose_name='vanaf vandaag')
    stop = models.DateTimeField(blank=True,null=True)
    percount = models.IntegerField(default=2,verbose_name='aantal perioden',help_text='maximaal aantal periodes terug in de tijd (0 = alle perioden)')
    perunit = models.CharField(max_length=10,choices = PERIOD_CHOICES, default = 'months', verbose_name='periodelengte')
    timezone = models.CharField(max_length=20,choices=TIMEZONE_CHOICES,verbose_name='tijdzone',blank=True)

    def tijdreeksen(self):
        return self.series.count()
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('acacia:chart-view', args=[self.pk])

    def get_dash_url(self):
        return reverse('acacia:chart-detail', args=[self.pk])

    def get_theme(self):
        for s in self.series.all():
            return s.theme()
        return None
    
    def auto_start(self):
        if self.start is None:
            start = aware(datetime.datetime.now(),self.timezone)
            for cs in self.series.all():
                t0 = cs.t0
                if t0 is None:
                    t0 = cs.series.van()
                if t0 is not None:
                    start = min(t0,start)
            if self.percount > 0:
                kwargs = {self.perunit: -self.percount}
                delta = dateutil.relativedelta.relativedelta(**kwargs)
                pstart = aware(datetime.datetime.now() + delta, self.timezone)
                if start is None:
                    return pstart
                start = max(start,pstart) 
            return start
        return self.start

    def to_pandas(self,**kwargs):
        s = { unicode(cd.series)+('' if cd.series.validated else '*'): cd.series.to_pandas(**kwargs) for cd in self.series.all() }
        return pd.DataFrame(s)
    
    def to_csv(self,**kwargs):
        io = StringIO.StringIO()
        df = self.to_pandas(**kwargs)
        df.to_csv(io,index_label='Datum/tijd')
        return io.getvalue()
        
    class Meta:
        ordering = ['name',]
        verbose_name = 'Grafiek'
        verbose_name_plural = 'Grafieken'

@receiver(pre_save, sender=Chart)
def chart_pre_save(sender, instance, **kwargs):
    if not instance.timezone:
        instance.timezone = get_current_timezone()

class Grid(Chart):    
    colwidth = models.FloatField(default=1,verbose_name='tijdstap',help_text='tijdstap in uren')
    rowheight = models.FloatField(default=1,verbose_name='rijhoogte')
    ymin = models.FloatField(default=0,verbose_name='y-minimum')
    entity = models.CharField(default='Weerstand', max_length=50, verbose_name='grootheid')
    unit = models.CharField(max_length=20,default='Ωm',blank=True,verbose_name='eenheid')
    zmin = models.FloatField(null=True,blank=True,verbose_name='z-minimum')
    zmax = models.FloatField(null=True,blank=True,verbose_name='z-maximum')
    scale = models.FloatField(default=1.0,verbose_name='verschalingsfactor')
    
    def get_absolute_url(self):
        return reverse('acacia:grid-view', args=[self.pk])

    def get_dash_url(self):
        return reverse('acacia:grid-detail', args=[self.pk])

    def get_extent(self):
        x1 = None
        x2 = None
        y1 = self.ymin
        y2 = y1 + max(0,self.series.count()-1) * self.rowheight
        z1 = None
        z2 = None
        for cs in self.series.all():
            s = cs.series
            if x1 is None:
                x1 = s.van()
                x2 = s.tot()
                z1 = s.minimum()
                z2 = s.maximum()
            else:
                x1 = min(x1,s.van())
                x2 = max(x2,s.tot())
                z1 = min(z1,s.minimum())
                z2 = max(z2,s.maximum())
        if self.start is not None:
            x1 = self.start
        if self.stop is not None:
            x2 = self.stop
        if self.zmin is not None:
            z1 = self.zmin
        else:
            z1 *= self.scale
        if self.zmax is not None:
            z2 = self.zmax
        else:
            z2 *= self.scale
        return (x1,y1,z1,x2,y2,z2)

DASHSTYLES = (('Solid', 'Standaard'),
              ('Dash', 'Gestreept'),
              ('Dot', 'Gestippeld'),
              )
ORIENTATION = (('h', 'horizontaal'), ('v','vertikaal'))              
dashStyles = [
        'Solid',
        'ShortDash',
        'ShortDot',
        'ShortDashDot',
        'ShortDashDotDot',
        'Dot',
        'Dash',
        'LongDash',
        'DashDot',
        'LongDashDot',
        'LongDashDotDot'
    ]
class BandStyle(models.Model):
    name = models.CharField(max_length=32,verbose_name='naam')
    fillcolor = models.CharField(max_length=32,verbose_name='achtergrondkleur')
    bordercolor = models.CharField(max_length=32,default='black',verbose_name='randkleur')
    borderwidth = models.IntegerField(default=0,verbose_name='breedte rand')
    zIndex = models.IntegerField(default = 0,verbose_name='volgorde')

    def __unicode__(self):
        return self.name
    
class LineStyle(models.Model):
    name = models.CharField(max_length=32,verbose_name='naam')
    color = models.CharField(max_length=32,default='black',verbose_name='kleur')
    dashstyle = models.CharField(max_length=32,default='Solid',choices=DASHSTYLES,verbose_name='stijl')
    width = models.CharField(max_length=32,default='0',verbose_name='breedte')
    zIndex = models.IntegerField(default = 0,verbose_name='volgorde')

    def __unicode__(self):
        return self.name


class PlotLine(models.Model):
    chart = models.ForeignKey(Chart,verbose_name='grafiek')
    axis = models.IntegerField(default=1)
    style = models.ForeignKey(LineStyle,verbose_name='stijl')
    orientation = models.CharField(max_length=1,choices=ORIENTATION,verbose_name='oriëntatie')
    label = models.CharField(max_length=50)
    value = models.CharField(max_length=32,verbose_name='waarde')
    repetition = models.CharField(max_length=32,default='0',verbose_name='herhaling')

    class Meta:
        verbose_name = 'Lijn'
        verbose_name_plural = 'Lijnen'
        
        
class PlotBand(models.Model):
    chart = models.ForeignKey(Chart,verbose_name='grafiek')
    axis = models.IntegerField(default=1)
    style = models.ForeignKey(BandStyle,verbose_name='stijl')
    orientation = models.CharField(max_length=1,choices=ORIENTATION,verbose_name='oriëntatie')
    label = models.CharField(max_length=50)
    low = models.CharField(max_length = 32,verbose_name='van')
    high = models.CharField(max_length=32,verbose_name='tot')
    repetition = models.CharField(max_length=32,verbose_name='herhaling')

    class Meta:
        verbose_name = 'Strook'
        verbose_name_plural = 'Stroken'

AXIS_CHOICES = (
                ('l', 'links'),
                ('r', 'rechts'),
               )

class ChartSeries(models.Model):
    chart = models.ForeignKey(Chart,related_name='series', verbose_name='grafiek')
    order = models.IntegerField(default=1,verbose_name='volgorde')
    series = models.ForeignKey(Series, verbose_name = 'tijdreeks')
    series2 = models.ForeignKey(Series, related_name='series2',blank=True, null=True, verbose_name = 'tweede tijdreeks', help_text='tijdreeks voor ondergrens bij area grafiek')
    name = models.CharField(max_length=100,blank=True,null=True,verbose_name='legendanaam')
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
        return unicode(self.series)
    
    def theme(self):
        s = self.series
        return None if s is None else s.theme()

    class Meta:
        ordering = ['order', 'name',]
        verbose_name = 'tijdreeks'
        verbose_name_plural = 'tijdreeksen'

class Dashboard(models.Model):
    name = models.CharField(max_length=100, verbose_name= 'naam')
    description = models.TextField(blank=True, null=True,verbose_name = 'omschrijving')
    charts = models.ManyToManyField(Chart, verbose_name = 'grafieken', through='DashboardChart')
    user=models.ForeignKey(User)
    
    def grafieken(self):
        return self.charts.count()

    def sorted_charts(self):
        return self.charts.order_by('dashboardchart__order')
    
    def get_absolute_url(self):
        return reverse('acacia:dash-view', args=[self.id]) 

    def __unicode__(self):
        return self.name
    
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
    name = models.CharField(max_length = 50, verbose_name='naam', help_text='naam van dashboard groep')

    def pagecount(self):
        return self.tabpage_set.count()
    pagecount.short_description = 'aantal tabs'
    
    def pages(self):
        return self.tabpage_set.order_by('order')
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('acacia:tabgroup', args=[self.id]) 

    class Meta:
        verbose_name = 'Dashboardgroep'
        verbose_name_plural = 'Dashboardgroepen'
        
class TabPage(models.Model):
    tabgroup = models.ForeignKey(TabGroup)
    name = models.CharField(max_length=50,default='basis',verbose_name='naam')
    order = models.IntegerField(default=1,verbose_name='volgorde', help_text='volgorde van tabblad')
    dashboard = models.ForeignKey(Dashboard)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Tabblad'
        verbose_name_plural = 'Tabbladen'
        
class CalibrationData(models.Model):
    datasource = models.ForeignKey(Datasource)
    parameter = models.ForeignKey(Parameter)
    sensor_value = models.FloatField(verbose_name = 'meetwaarde')
    calib_value = models.FloatField(verbose_name='ijkwaarde')
    
    class Meta:
        verbose_name = 'IJkpunt'        
        verbose_name_plural = 'IJkset'

class KeyFigure(models.Model):
    ''' Net zoiets als een Formula, maar dan met een scalar als resultaat'''
    locatie = models.ForeignKey(MeetLocatie)
    name = models.CharField(max_length=200, verbose_name = 'naam')
    description = models.TextField(blank=True, null = True, verbose_name = 'omschrijving')
    variables = models.ManyToManyField(Variable,verbose_name = 'variabelen')
    formula = models.TextField(blank=True,null=True,verbose_name = 'berekening')
    last_update = models.DateTimeField(auto_now = True, verbose_name = 'bijgewerkt')
    startDate = models.DateField(blank=True, null=True)
    stopDate = models.DateField(blank=True, null=True)
    value = models.FloatField(blank=True, null=True, verbose_name = 'waarde')
    
    def __unicode__(self):
        return self.name

    def get_variables(self):
        variables = {var.name: var.series.to_pandas() for var in self.variables.all()}
        df = pd.DataFrame(variables)
        start = max([v.index.min() for v in variables.values()])
        stop = min([v.index.max() for v in variables.values()])
        if self.startDate:
            start = self.startDate
        if self.stopDate:
            stop = self.stopDate
        df = df[start:stop]
        df = df.interpolate(method='time')
        return df.to_dict('series')

    def get_value(self):
        variables = self.get_variables()
        result = eval(self.formula, globals(), variables)
        if isinstance(result, pd.DataFrame):
            result = result[0]
        elif isinstance(result, pd.Series):
            result.name = self.name
        return result
    
    def update(self):
        self.value = self.get_value()
        self.save(update_fields=['value'])
        return self.value

    class Meta:
        verbose_name = 'Kental'        
        verbose_name_plural = 'Kentallen'
        unique_together = ('locatie', 'name')
