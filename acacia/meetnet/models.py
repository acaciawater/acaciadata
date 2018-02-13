'''
Created on Jun 1, 2014

@author: theo
'''
import os, pandas as pd, numpy as np
from django.db import models
from django.contrib.gis.db import models as geo
from django.core.urlresolvers import reverse
from acacia.data.models import Datasource, Series, SourceFile, ProjectLocatie,\
    MeetLocatie, ManualSeries
from acacia.data import util
from django.db.models.aggregates import Count
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.db.models.deletion import SET_NULL

class Network(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name = _('name'))
    logo = models.ImageField(upload_to='logos')
    homepage = models.URLField(blank=True, help_text = _('website of netork administrator'))
    bound = models.URLField(blank=True,verbose_name = 'grens', help_text = _('url of kml file of network boundary'))
    last_round = models.DateField(null=True,blank=True,verbose_name = _('last measuring round'))
    next_round = models.DateField(null=True,blank=True,verbose_name = _('next measuring round'))
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('meetnet:network-detail', args=[self.id])

    class Meta:
        verbose_name = _('network')
        verbose_name_plural = _('networks')


class Well(geo.Model):
    #TODO: this class should inherit from acacia.data.models.ProjectLocatie
    ploc = models.ForeignKey(ProjectLocatie, null=True, blank=True)
    network = models.ForeignKey(Network, verbose_name = _('network'))
    name = models.CharField(max_length=50, verbose_name = _('name'))
    nitg = models.CharField(max_length=50, verbose_name = _('TNO/NITG identification'), null=True, blank=True)
    bro = models.CharField(max_length=50, verbose_name = _('BRO id'), null=True, blank=True)
    location = geo.PointField(null=True,dim=2,srid=util.WGS84,verbose_name=_('location'), help_text=_('Location in longitude/latitude coordinates'))

    description = models.TextField(verbose_name=_('description'),null=True,blank=True)
    maaiveld = models.FloatField(null=True, blank=True, verbose_name = _('surface level'), help_text = _('surface level in meter wrt NAP'))
    ahn = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=10, verbose_name = _('AHN surface level'))
    date = models.DateField(null=True, blank=True, verbose_name = _('Date of construction'))
    owner = models.CharField(max_length=40,blank=True,null=True,verbose_name=_('owner'))
    straat = models.CharField(max_length=60, null=True, blank=True,verbose_name=_('street name'))
    huisnummer = models.CharField(max_length=12, null=True, blank=True,verbose_name=_('house number'))
    postcode = models.CharField(max_length=8, null=True, blank=True,verbose_name=_('postal code'))
    plaats = models.CharField(max_length=60, null=True, blank=True,verbose_name=_('locality'))
    log = models.ImageField(null=True, blank=True, upload_to='logs',verbose_name=_("driller's log"))
    chart = models.ImageField(null=True,blank=True, upload_to='charts', verbose_name=_('chart'))
    g = models.FloatField(default=9.80665,verbose_name=_('gravitational acceleration'), help_text=_('gravitational acceleration in m/s2'))
    objects = geo.GeoManager()
    
    def latlon(self):
        return util.toWGS84(self.location)

    def RD(self):
        return util.toRD(self.location)

    def num_filters(self):
        return self.screen_set.count()
    num_filters.short_description=_('number of screens')

    def num_photos(self):
        return self.photo_set.count()
    num_photos.short_description=_('number of photos')

    def _openimage(self, fp, fmt='JPEG'):
        ''' opens image from file-like object while honoring rotation tag '''
        from PIL import Image
        from cStringIO import StringIO

        ORIENTATION = 274
        TRANSPOSE = {3: Image.ROTATE_180, 6: Image.ROTATE_270, 8: Image.ROTATE_90}
        
        image = Image.open(fp)
        try:
            exif = image._getexif()
            if exif and ORIENTATION in exif:
                orientation = exif[ORIENTATION]
                if orientation in TRANSPOSE:
                    image = image.transpose(TRANSPOSE[orientation])
                    io = StringIO()
                    image.save(io,fmt)
                    fp = io
        except:
            pass
        return fp
    
    def add_photo(self, name, fp, fmt='JPEG'):
        ''' adds or replaces photo '''
        fp = self._openimage(fp, fmt)
        basename,_ext = os.path.splitext(name)
        queryset = self.photo_set.filter(photo__contains=basename)
        if queryset:
            photo_obj = queryset.first()
        else:
            photo_obj = self.photo_set.create() 
        photo_obj.photo.save(name,fp,save=True)
        
    def set_log(self, name, fp, fmt='JPEG'):
        ''' sets or replaces borelog '''
        fp = self._openimage(fp, fmt)
        self.log.save(name,fp,save=True)
        
    def full_address(self,sep=', '):
        def add(a,b,sep):
            if b:
                if a:
                    a += sep
                    a += b
                else:
                    a = b
            return a
        
        adres = add(self.straat,self.huisnummer,' ')
        adres = add(adres, self.postcode, ', ')
        adres = add(adres, self.plaats, ' ')
        return adres
    
    def get_absolute_url(self):
        return reverse('meetnet:well-detail', args=[self.id])

    def __unicode__(self):
        #return self.nitg or self.name
        return self.name
    
    def has_data(self):
        for s in self.screen_set.all():
            if s.has_data():
                return True
        return False
    
    def last_measurement(self):
        last = [s.last_measurement() for s in self.screen_set.all()]
        if last:
            # remove None measurements
            last = [m for m in last if m]
            if last:
                return max(last,key=lambda x: x.date)
        return None
    
    def last_measurement_date(self):
        last = self.last_measurement()
        return last.date.date() if last else None
    
    class Meta:
        verbose_name = _('well')
        verbose_name_plural = _('wells')
        ordering = ['name','nitg']
        unique_together = ('name','nitg')
        
def limitKNMI():
    return {'parameter__datasource__generator__classname__icontains':'KNMI'}

class MeteoData(models.Model):
    """ meteo data for a well """
    well = models.OneToOneField(Well,related_name='meteo',verbose_name=_('well'))
    baro = models.ForeignKey(Series,on_delete=models.SET_NULL,blank=True,null=True,related_name='well_baro',limit_choices_to=limitKNMI,verbose_name=_('air pressure'))
    neerslag = models.ForeignKey(Series,on_delete=models.SET_NULL,blank=True,null=True,related_name='well_p',limit_choices_to=limitKNMI,verbose_name=_('precipitation'))
    verdamping = models.ForeignKey(Series,on_delete=models.SET_NULL,blank=True,null=True,related_name='well_ev24',limit_choices_to=limitKNMI,verbose_name=_('evaporation'))
    temperatuur = models.ForeignKey(Series,on_delete=models.SET_NULL,blank=True,null=True,related_name='well_temp',limit_choices_to=limitKNMI,verbose_name=_('temperature'))

    def __unicode__(self):
        return unicode(self.well)
    
    class Meta:
        verbose_name = _('meteo')
        verbose_name_plural = _('Meteo')

class Photo(models.Model): 
    # TODO: use sorl.thumbnail?
    well = models.ForeignKey(Well)
    photo = models.ImageField(upload_to = 'fotos') 
    
    def thumb(self):
        url = self.photo.url
        return '<a href="%s"><img src="%s" height="60px"/></a>' % (url,url)

    def __unicode__(self):
        try:
            return os.path.basename(self.photo.file.name)
        except:
            return ' '

    thumb.allow_tags=True
    thumb.short_description=_('sample')

    class Meta:
        verbose_name = _('photo')
        verbose_name_plural = _('photos')
    
MATERIALS = (
             ('pvc', _('PVC')),
             ('hdpe', _('HDPE')),
             ('ss', _('SS')),
             ('ms', _('steel')),
             )                  
class Screen(models.Model):
    mloc = models.ForeignKey(MeetLocatie, null=True, blank=True)
    well = models.ForeignKey(Well, verbose_name = _('well'))
    nr = models.IntegerField(default=1, verbose_name = _('screen number'))
    density = models.FloatField(default=1000.0,verbose_name=_('density'),help_text=_('density of the water in observation tube (kg/m3)'))
    refpnt = models.FloatField(null=True, blank=True, verbose_name = _('top of casing'), help_text = _('top of casing in m wrt NAP'))
    depth = models.FloatField(null=True, blank=True, verbose_name = _('depth'), help_text = _('depth of pipe in meters below the surface'))
    top = models.FloatField(null=True, blank=True, verbose_name = _('top of screen'), help_text = _('top of screen in meters below the surface'))
    bottom = models.FloatField(null=True, blank=True, verbose_name = _('bottom of screen'), help_text = _('bottom of screen in meters below the surface'))
    diameter = models.FloatField(null=True, blank=True, verbose_name = _('diameter'), default=32, help_text=_('diameter in mm (default = 32 mm)'))
    material = models.CharField(blank=True, max_length = 10,verbose_name = _('material'), default='pvc', choices = MATERIALS)
    chart = models.ImageField(null=True,blank=True, upload_to='charts', verbose_name=_('chart'))
    aquifer = models.CharField(max_length=20,blank=True,null=True,verbose_name=_('aquifer'))
    manual_levels = models.ForeignKey(Series, null=True, blank=True, on_delete=SET_NULL, verbose_name=_('manual measurements'), related_name='manual')
    logger_levels = models.ForeignKey(Series, null=True, blank=True, on_delete=SET_NULL, verbose_name=_('water level'), related_name='waterlevel')

    def get_series(self, ref = 'nap', kind='COMP', **kwargs):
        
        def bydate(record):
            return record[0]

        # luchtdruk gecompenseerde standen (tov NAP) ophalen
        rule = kwargs.pop('rule',None)
        series = self.get_manual_series(**kwargs) if kind == 'HAND' else self.get_compensated_series(**kwargs)
        if series is None or series.empty:
            return []

        if rule:
            # resample timeseries
            series = series.resample(rule=rule).mean()
            nans = series[pd.isnull(series)]

        levels = []
        for index,value in series.iteritems():
            try:
                if pd.isnull(value):
                    level = None
                elif ref == 'nap':
                    level = value
                elif ref == 'bkb':
                    level = self.refpnt - value
                elif ref == 'mv':
                    level = self.well.maaiveld - value
                else:
                    raise _('Illegal reference for screen %s') % unicode(self)
                levels.append((index, level))
            except:
                pass # refpnt, maaiveld or value is None
        levels.sort(key=bydate)
        return levels

    def get_levels(self, ref='nap', **kwargs):
        return self.get_series(ref,kind='COMP',**kwargs)        

    def get_hand(self, ref='nap', **kwargs):
        return self.get_series(ref,kind='HAND',**kwargs)        
        
    def get_monfiles(self):
        return MonFile.objects.filter(source__screen=self).order_by('start_date')
#         files = []
#         for lp in self.loggerpos_set.order_by('start_date'):
#             files.extend(lp.monfile_set.order_by('start_date'))
#         return files

    def num_files(self):
        try:
            query = self.mloc.datasource_set.aggregate(Count('sourcefiles'))
            return query['sourcefiles__count']
        except:
            return 0
        
    def find_series(self):
        if not self.logger_levels:
            from django.db.models import Q
            series = self.mloc.series_set.filter(Q(name__iendswith='comp')|Q(name__istartswith='waterstand')|Q(name__iendswith='value')).first()
            if series:
                self.logger_levels = series
                self.save()
        return self.logger_levels
    
    def start(self):
        try:
            return self.find_series().van()
        except:
            return None

    def stop(self):
        try:
            return self.find_series().tot()
        except:
            return None
        
    def num_standen(self):
        try:
            s = self.find_series()
            return s.aantal()
            #return self.find_series().aantal()
        except:
            return 0
        
    def has_data(self):
        return self.num_standen()>0

        
    def get_loggers(self):
        # Not supported by MySQL:
        # return [p.logger for p in self.loggerpos_set.order_by('logger__serial').distinct('logger__serial')]
        d = {p.logger.serial:p.logger for p in self.loggerpos_set.all()}
        return d.values()
        
    def last_logger(self):
        last = self.loggerpos_set.all().order_by('start_date').last()
        #return None if last is None else last.logger
        return last
    
    def __unicode__(self):
        #return '%s/%03d' % (self.well.nitg, self.nr)
        wid = self.well.nitg or self.well.name
        return '%s/%03d' % (wid, self.nr)

    def get_absolute_url(self):
        return reverse('meetnet:screen-detail', args=[self.pk])

    def to_pandas(self, ref='nap',kind='COMP',**kwargs):
        levels = self.get_series(ref,kind,**kwargs)
        if len(levels) > 0:
            x,y = zip(*levels)
        else:
            x = []
            y = []
        return pd.Series(index=x, data=y, name=unicode(self))
        
    def get_manual_series(self, **kwargs):
        if not self.manual_levels: 
            # Handpeilingen ophalen
            for s in self.mloc.series_set.instance_of(ManualSeries):
                if s.name.endswith('HAND'):
                    self.manual_levels = s
                    self.save()
            return None
        return self.manual_levels.to_pandas(**kwargs)
            
    def get_compensated_series(self, **kwargs):
        # Gecompenseerde tijdreeksen (tov NAP) ophalen (Alleen voor Divers and Leiderdorp Instruments)
        try:
            series = self.find_series()
            return series.to_pandas(**kwargs) if series else None
        except Exception as e:
            return None
    
    def stats(self):
        df = self.get_compensated_series()
        if df is None:
            return {}
        s = df.describe(percentiles=[.1,.5,.9])
        s['p10'] = None if np.isnan(s['10%']) else s['10%']
        s['p50'] = None if np.isnan(s['50%']) else s['50%']
        s['p90'] = None if np.isnan(s['90%']) else s['90%']
        return s
        
    def last_measurement(self):
        series = self.find_series()
        if series and series.datapoints:
            return series.datapoints.latest('date')
        else:
            return None
        
    class Meta:
        unique_together = ('well', 'nr',)
        verbose_name = _('screen')
        verbose_name_plural = _('screens')
        ordering = ['well', 'nr',]
        
DIVER_TYPES = (
               ('micro','Micro-Diver'),
               ('3', 'TD-Diver'),
               ('ctd','CTD-Diver'),
               ('16','Cera-Diver'),
               ('14','Mini-Diver'),
               ('baro','Baro-Diver'),
               ('etd','ElliTrack-D'),
               ('etd2','ElliTrack-D2'), # voor in straatpot
               )
class Datalogger(models.Model):
    serial = models.CharField(max_length=50,verbose_name = _('serial number'),unique=True)
    model = models.CharField(max_length=50,verbose_name = _('type'), default='14', choices=DIVER_TYPES)
    
    def __unicode__(self):
        return self.serial
 
    class Meta:
        ordering = ['serial']

class LoggerPos(models.Model):
    logger = models.ForeignKey(Datalogger)
    screen = models.ForeignKey(Screen,verbose_name = _('screen'),blank=True, null=True)
    start_date = models.DateTimeField(verbose_name = _('start'), help_text = _('Start of datalogger'))   
    end_date = models.DateTimeField(verbose_name = _('stop'), blank=True, null=True, help_text = _('Stopping time of datalogger'))   
    refpnt = models.FloatField(verbose_name = _('reference point'), blank=True, null=True, help_text = _('Reference point in meter wrt NAP'))
    depth = models.FloatField(verbose_name = _('cable length'), blank=True, null=True, help_text = _('length of cable in meter'))
    remarks = models.TextField(verbose_name=_('remarks'), blank=True) 

    def __unicode__(self):
        return '%s@%s' % (self.logger, self.screen)
    
    class Meta:
        verbose_name = _('LoggerInstallation')
        ordering = ['start_date','logger']

    def stats(self):
        try:
            s = self.loggerstat
        except ObjectDoesNotExist:
            s = LoggerStat.objects.create(loggerpos = self)
        if s.count == 0:
            s.update()
        return s
    
    def clear_stats(self):
        try:
            s = self.loggerstat
            s.count = 0 # will cause automatic update
            s.save()
        except ObjectDoesNotExist:
            pass
    
    def num_monfiles(self):
        return self.monfile_set.count()
    num_monfiles.short_description = _('Monfiles')
    
class LoggerStat(models.Model):
    loggerpos = models.OneToOneField(LoggerPos)
    count = models.PositiveIntegerField(default=0)
    min = models.FloatField(default=0,blank=True,null=True)
    p10 = models.FloatField(default=0,blank=True,null=True)
    p50 = models.FloatField(default=0,blank=True,null=True)
    p90 = models.FloatField(default=0,blank=True,null=True)
    max = models.FloatField(default=0,blank=True,null=True)
    std = models.FloatField(default=0,blank=True,null=True)

    def update(self):
        df = self.loggerpos.screen.get_compensated_series(start=self.loggerpos.start_date, stop = self.loggerpos.end_date)
        if df is None or df.empty:
            return
        s = df.describe(percentiles=[.1,.5,.9])
        self.count = None if np.isnan(s['count']) else s['count']
        self.min = None if np.isnan(s['min']) else s['min']
        self.p10 = None if np.isnan(s['10%']) else s['10%']
        self.p50 = None if np.isnan(s['50%']) else s['50%']
        self.p90 = None if np.isnan(s['90%']) else s['90%']
        self.max = None if np.isnan(s['max']) else s['max']
        self.std = None if np.isnan(s['std']) else s['std']
        self.save()
        
class LoggerDatasource(Datasource):
    logger = models.ForeignKey(Datalogger, related_name = 'datasources')
     
    class Meta:
        verbose_name = 'Loggerdata'
        verbose_name_plural = 'Loggerdata'
        
    def build_download_options(self, start=None):
        # add logger name to download options
        options = Datasource.build_download_options(self, start=start)
        if options is not None:
            options['logger'] = unicode(self.logger)
        return options

class MonFile(SourceFile):
    company = models.CharField(max_length=50)
    compstat = models.CharField(max_length=10)
    date = models.DateTimeField()
    monfilename = models.CharField(verbose_name='Filename',max_length=512)
    createdby = models.CharField(max_length=100)
    instrument_type = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    serial_number = models.CharField(max_length=50)
    instrument_number = models.CharField(blank=True,null=True,max_length=50)
    location = models.CharField(max_length=50)
    sample_period = models.CharField(max_length=50)
    sample_method = models.CharField(max_length=10)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    num_channels = models.IntegerField(default = 1)
    num_points = models.IntegerField()

    source = models.ForeignKey(LoggerPos,verbose_name='diver',blank=True,null=True)

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

    class Meta:
        verbose_name = 'Kanaal'
        verbose_name_plural = 'Kanalen'
        
HAND_CHOICES=(
    ('bkb',_('Top of casing')),
    ('nap',_('NAP')),
    )

class Handpeiling(ManualSeries):
    screen = models.ForeignKey(Screen,on_delete=models.CASCADE,verbose_name=_('screen')) 
    refpnt = models.CharField(max_length=4,choices=HAND_CHOICES,verbose_name=_('reference point'),default='bkb')

    class Meta:
        verbose_name = 'Handpeiling'
        verbose_name_plural = 'Handpeilingen'
    