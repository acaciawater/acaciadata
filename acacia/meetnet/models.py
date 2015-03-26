'''
Created on Jun 1, 2014

@author: theo
'''
import os, pandas as pd, numpy as np
from django.db import models
from django.contrib.gis.db import models as geo
from django.core.urlresolvers import reverse
from acacia.data.models import Datasource, Series, SourceFile
from acacia.data import util

class Network(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name = 'naam')
    logo = models.ImageField(upload_to='logos')
    homepage = models.URLField(blank=True, help_text = 'website van meetnetbeheerder')
    bound = models.URLField(blank=True,verbose_name = 'grens', help_text = 'url van kml file met begrenzing van het meetnet')
    last_round = models.DateField(null=True,blank=True,verbose_name = 'laatste uitleesronde')
    next_round = models.DateField(null=True,blank=True,verbose_name = 'volgende uitleesronde')
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('network-detail', args=[self.id])

    class Meta:
        verbose_name = 'netwerk'
        verbose_name_plural = 'netwerken'

class Well(geo.Model):
    network = models.ForeignKey(Network, verbose_name = 'Meetnet')
    name = models.CharField(max_length=50, unique=True, verbose_name = 'naam')
    nitg = models.CharField(max_length=50, verbose_name = 'TNO/NITG nummer', blank=True)
    bro = models.CharField(max_length=50, verbose_name = 'BRO nummer', blank=True)
    location = geo.PointField(srid=28992,verbose_name='locatie')
    maaiveld = models.FloatField(verbose_name = 'maaiveld', help_text = 'maaiveld in meter tov NAP')
    refpnt = models.FloatField(verbose_name = 'referentiepunt', help_text='referentiepunt in meter tov NAP')
    date = models.DateField(verbose_name = 'constructiedatum')
    straat = models.CharField(max_length=60, blank=True)
    huisnummer = models.CharField(max_length=6, blank=True)
    postcode = models.CharField(max_length=8, blank=True)
    plaats = models.CharField(max_length=60, blank=True)
    log = models.ImageField(null=True,blank=True,upload_to='logs',verbose_name = 'boorstaat')
    chart = models.ImageField(null=True,blank=True, upload_to='charts', verbose_name='grafiek')
    objects = geo.GeoManager()

    def latlon(self):
        return util.toWGS84(self.location)

    def RD(self):
        return util.toRD(self.location)

    def num_filters(self):
        return self.screen_set.count()
    num_filters.short_description='aantal filters'

    def num_photos(self):
        return self.photo_set.count()
    num_photos.short_description='aantal fotos'

    def get_loggers(self):
        loggers = []
        for s in self.screen_set.all():
            loggers.extend(s.datalogger_set.all())
        return loggers
    
    def num_loggers(self):
        return len(self.get_loggers())
    num_loggers.short_description='aantal dataloggers'
    
    def logger_names(self):
        return ','.join([l.serial for l in self.get_loggers()])
    logger_names.short_description='dataloggers'
    
    def get_absolute_url(self):
        return reverse('well-detail', args=[self.id])

    def __unicode__(self):
        return self.name
    
    def has_data(self):
        for s in self.screen_set.all():
            if s.has_data():
                return True
        return False
    
    class Meta:
        verbose_name = 'put'
        verbose_name_plural = 'putten'
        ordering = ['name',]

class Photo(models.Model): 
    well = models.ForeignKey(Well)
    photo = models.ImageField(upload_to = 'fotos') 
    
    def thumb(self):
        url = self.photo.url
        return '<a href="%s"><img src="%s" height="60px"/></a>' % (url,url)

    def __unicode__(self):
        return os.path.basename(self.photo.file.name)

    thumb.allow_tags=True
    thumb.short_description='voorbeeld'

    class Meta:
        verbose_name = 'foto'
        verbose_name_plural = "foto's"
    
MATERIALS = (
             ('pvc', 'PVC'),
             ('hdpe', 'HDPE'),
             ('ss', 'RVS'),
             ('ms', 'Staal'),
             )                  
class Screen(models.Model):
    well = models.ForeignKey(Well, verbose_name = 'put')
    nr = models.IntegerField(default=1, verbose_name = 'filternummer')
    top = models.FloatField(verbose_name = 'bovenkant', help_text = 'bovenkant filter in meter min maaiveld')
    bottom = models.FloatField(verbose_name = 'onderkant', help_text = 'onderkant filter in meter min maaiveld')
    diameter = models.FloatField(verbose_name = 'diameter', default=32, help_text='diameter in mm (standaard = 32 mm)')
    material = models.CharField(max_length = 10,verbose_name = 'materiaal', default='pvc', choices = MATERIALS)
    chart = models.ImageField(null=True,blank=True, upload_to='charts', verbose_name='grafiek')

    def get_series(self):
        series = []
        for logger in self.datalogger_set.all():
            for ds in logger.datasources.all():
                series.extend(ds.getseries())
        return series
    
    def get_parameter_series(self, name):
        series = []
        for logger in self.datalogger_set.all():
            for ds in logger.datasources.all():
                for p in ds.parameter_set.filter(name=name):
                    for s in p.series_set.all():
                        series.append(s)
        return series
    
    def get_pressure(self):
        return self.get_parameter_series('PRESSURE')

    def get_levels(self, ref='nap', formula='LEVEL'):
        series = []
        for logger in self.datalogger_set.all():
            for ds in logger.datasources.all():
                meetlocatie = ds.meetlocatie
                for s in meetlocatie.formula_set.filter(name=formula):
                    for dp in s.datapoints.all():
                        level = dp.value / 100
                        if ref == 'ref':
                            # m h2o -> m tov refpnt
                            level = logger.depth - level
                        elif ref == 'nap':
                            # m h2o -> m tov nap
                            level = level + (logger.refpnt - logger.depth)
                        elif ref == 'mv':
                            level = level + (logger.refpnt - logger.depth - self.well.maaiveld)
                        series.append((dp.date, level))
        return series

    def get_monfiles(self):
        files = []
        for logger in self.datalogger_set.all():
            for ds in logger.datasources.all():
                files.extend(list(ds.sourcefiles.all()))
        return files

    def num_files(self):
        files = 0
        for logger in self.datalogger_set.all():
            for ds in logger.datasources.all():
                files += ds.filecount() or 0
        return files
    
    def num_standen(self):
        files = self.get_monfiles()
        return sum([f.rows for f in files]) if len(files)> 0 else 0

    def has_data(self):
        return self.num_standen() > 0

    def start(self):
        files = self.get_monfiles()
        return min([f.start for f in files]) if len(files) > 0 else None

    def stop(self):
        files = self.get_monfiles()
        return max([f.stop for f in files]) if len(files) > 0 else None
        
    def last_logger(self):
        return self.datalogger_set.all().order_by('date').last()
        
    def __unicode__(self):
        return '%s/%03d' % (self.well, self.nr)

    def get_absolute_url(self):
        return reverse('screen-detail', args=[self.id])

    def to_pandas(self, ref='nap'):
        levels = self.get_levels(ref)
        if len(levels) > 0:
            x,y = zip(*levels)
        else:
            x = []
            y = []
        return pd.Series(index=x, data=y, name=unicode(self))
        
    def stats(self):
        df = self.to_pandas()
        s = df.describe(percentiles=[.1,.5,.9])
        s['p10'] = None if np.isnan(s['10%']) else s['10%']
        s['p50'] = None if np.isnan(s['50%']) else s['50%']
        s['p90'] = None if np.isnan(s['90%']) else s['90%']
        return s
        
    class Meta:
        unique_together = ('well', 'nr',)
        verbose_name = 'filter'
        verbose_name_plural = 'filters'
        ordering = ['well', 'nr',]
        
DIVER_TYPES = (
               ('micro','Micro-Diver'),
               ('td', 'TD-Diver'),
               ('ctd','CTD-Diver'),
               ('cera','Cera-Diver'),
               ('mini','Mini-Diver'),
               ('baro','Baro-Diver')
               )
class Datalogger(models.Model):
    serial = models.CharField(max_length=50,verbose_name = 'serienummer', unique=True)
    model = models.CharField(max_length=50,verbose_name = 'type', default='ctd', choices=DIVER_TYPES)
    screen = models.ForeignKey(Screen,verbose_name = 'filter',blank=True, null=True)
    date = models.DateTimeField(verbose_name = 'datum', help_text = 'Datum en tijd van installatie datalogger')
    refpnt = models.FloatField(verbose_name = 'referentiepunt', help_text = 'ophangpunt in meter tov NAP')
    depth = models.FloatField(verbose_name = 'kabellengte', help_text = 'lengte van ophangkabel in meter')
    baro = models.ForeignKey(Series, blank=True, null=True, verbose_name='barometer', help_text = 'barometer reeks voor luchtdruk compensatie')
    
    def __unicode__(self):
        return self.serial

    class Meta:
        ordering = ['serial',]

class LoggerDatasource(Datasource):
    logger = models.ForeignKey(Datalogger, related_name = 'datasources')
    
    class Meta:
        verbose_name = 'Gegevensbron'
        verbose_name_plural = 'Gegevensbronnen'

class MonFile(SourceFile):
    company = models.CharField(max_length=50)
    compstat = models.CharField(max_length=10)
    date = models.DateTimeField()
    monfilename = models.CharField(max_length=512)
    createdby = models.CharField(max_length=100)
    instrument_type = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    serial_number = models.CharField(max_length=50)
    instrument_number = models.CharField(max_length=50)
    location = models.CharField(max_length=50)
    sample_period = models.CharField(max_length=50)
    sample_method = models.CharField(max_length=10)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    num_channels = models.IntegerField(default = 1)
    num_points = models.IntegerField()
 
    def __unicode__(self):
        return self.monfilename
     
class Channel(models.Model):
    monfile = models.ForeignKey(MonFile)
    number = models.IntegerField()
    identification = models.CharField(max_length=20)
    reference_level = models.FloatField()
    reference_unit = models.CharField(max_length=10)
    range = models.FloatField()
    range_unit = models.CharField(max_length=10)
 
    def __unicode__(self):
        return self.identification
