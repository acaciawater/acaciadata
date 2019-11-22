# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your models here.

# This is an auto-generated Django model module created by ogrinspect.
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from acacia.meetnet.models import Well, Screen
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_init
from django.dispatch.dispatcher import receiver

class MapSheet(models.Model):
    '''
    Feature definition of mapsheets to determine mapsheet code from well location 
    '''
    area = models.FloatField()
    perimeter = models.FloatField()
    topo_2561_field = models.IntegerField()
    topo_25611 = models.IntegerField()
    bladnaam = models.CharField(max_length=20)
    nr = models.IntegerField()
    ltr = models.CharField(max_length=1)
    district = models.CharField(max_length=2)
    blad = models.CharField(max_length=3)
    geom = models.PolygonField(srid=28992)
    
    @classmethod
    def from_location(cls, location, srid=28992):
        ''' return mapsheet queryset for a location. 
        Location can be a geos.Point or (x,y) tuple. 
        When tuple is given, the srid is required '''
        if type(location) in [list,tuple]:
            point=Point(location,srid=srid)
        else:
            point=location
        point.transform(28992)
        return cls.objects.filter(geom__contains=point)

class Code(models.Model):
    ''' code from a urn:bro:gmw:CodeSpace '''
    codeSpace = models.CharField(_('codeSpace'),max_length=40)
    code = models.CharField(_('code'),max_length=40)
    is_default = models.BooleanField(default=False)
    
    @classmethod
    def get(cls,codeSpace,code):
        return cls.objects.get(codeSpace=codeSpace, code=code)
        
    def urn(self):    
        return 'urn:bro:gmw:{}:{}'.format(self.codeSpace, self.code)

    @classmethod
    def default(cls, codeSpace):
        q = cls.objects.filter(codeSpace=codeSpace, is_default = True)
        if q.count() == 1:
            return q.first()
        return None
    
    def __unicode__(self):
        return self.code
    
    class Meta:
        unique_together = ('codeSpace', 'code')

def CodeField(codeSpace, displayName=None, default=None):
    ''' BRO code implemented as ForeignKey '''

    return models.ForeignKey(Code,
                             on_delete=models.CASCADE,
                             related_name='+',
                             limit_choices_to={'codeSpace':codeSpace},
                             verbose_name=displayName or _(codeSpace),
#                             default=Code.get(codeSpace,default) if default else None
                            )
    
# class RegistrationRequest(models.Model):
#     requestReference = models.CharField(_('requestReference'),max_length=100)
#     deliveryAccountableParty = models.CharField(_('deliveryAccountableParty'),max_length=8)
#     broId = models.CharField(_('broid'),max_length=20)
#     qualityRegime = CodeField('qualityRegime',_('Kwaliteitsregime'))
#     underPrivilege = models.NullBooleanField(_('Onder voorrecht'))        

class GroundwaterMonitoringWell(models.Model):
    ''' Well data for BRO '''
    well = models.OneToOneField(Well,on_delete=models.CASCADE,related_name='bro')
    
    objectIdAccountableParty=models.CharField(_('ObjectID'),max_length=100)
    deliveryContext = CodeField('deliveryContext',_('Kader aanlevering'), default='publiekeTaak')
    constructionStandard = CodeField('constructionStandard',_('Kwaliteitsnorm inrichting'),default='onbekend')
    initialFunction = CodeField('initialFunction',_('Initiële functie'),default='stand')
    numberOfMonitoringTubes = models.PositiveIntegerField(_('Aantal monitoringbuizen'), default=1)
    groundLevelStable = models.NullBooleanField(_('Maaiveld stabiel'),default='onbekend')
    wellStability = models.NullBooleanField(_('Putstabiliteit'), max_length=16,default='onbekend')
    nitgCode = models.CharField(_('NITG code'),max_length=8,blank=True,null=True)
    mapSheetCode = models.CharField(_('Kaartblad'),max_length=3,blank=True,null=True)
    owner = models.CharField(_('Eigenaar'),max_length=8,help_text='KVK-nummer van de eigenaar')
    maintenanceResponsibleParty = models.CharField(_('Onderhoudende instantie'),max_length=8,null=True,blank=True)
    wellHeadProtector = CodeField('wellHeadProtector',_('Beschermconstructie'),default='onbekend')
    wellConstructionDate = models.DateField()
    deliveredLocation = models.PointField(_('Coordinaten'))
    horizontalPositioningMethod = CodeField('horizontalPositioningMethod', _('Methode locatiebepaling'), default='RTKGPS2tot5cm')
    deliveredVerticalPosition = models.FloatField(_('Maaiveld'))
    groundLevelPositioningMethod = CodeField('groundLevelPositioningMethod',_('Maaiveld positiebepaling'),default='RTKGPS0tot4cm')
    
    def __init__(self, *args, **kwargs):
        models.Model.__init__(self,*args, **kwargs)
        self.set_defaults((
            'deliveryContext',
            'constructionStandard',
            'initialFunction',
            'wellHeadProtector',
            'horizontalPositioningMethod',
            'groundLevelPositioningMethod'))

    def update(self):
        self.numberOfMonitoringTubes = self.well.screen_set.count()
        self.nitgCode = self.well.nitg
        sheets = MapSheet.from_location(self.well.location)
        self.mapSheetCode = next(sheets) if sheets else None 
        self.wellConstructionDate = self.well.date
        self.deliveredLocation = self.well.location
        self.deliveredVerticalPosition = self.well.maaiveld or self.well.ahn

    def set_defaults(self, fields):
        for fieldname in fields:
            if not hasattr(self, fieldname) or getattr(self,fieldname) is None:
                setattr(self,fieldname,Code.default(fieldname))
                        
class MonitoringTube(models.Model):
    ''' Screen data for BRO '''
    screen = models.OneToOneField(Screen,on_delete=models.CASCADE,related_name='bro')

    tubeNumber = models.PositiveSmallIntegerField(default = 1)
    tubeType = CodeField('tubeType', _('Buistype'))
    artesianWellCapPresent = models.NullBooleanField(_('Drukdop'))
    sedimentSumpPresent = models.NullBooleanField(_('Zandvang')) # True als diepte > onderkant filter
    numberOfGeoOhmCables = models.PositiveSmallIntegerField(default = 0)
    tubeTopDiameter = models.FloatField(_('Diameter'))
    variableDiameter = models.BooleanField(_('Variabele diameter'),default=False)
    tubeStatus = CodeField('tubeStatus', _('Status'))
    tubeTopPosition = models.FloatField(_('Bovenkant buis'))
    tubeTopPositioningMethod = CodeField('tubeTopPositioningMethod',_('Methode positiebepaling bovenkant buis'))
    tubePackingMaterial = CodeField('tubePackingMaterial',_('Aanvul materiaal'))
    materialUsed = CodeField('materialsUsed', _('Buismateriaal'))
    screenLength = models.FloatField(_('Filterlengte'))
    sockMaterial = CodeField('sockMaterial',_('Kousmateriaal'))
    plainTubePart = models.FloatField(_('Lengte stijgbuis'))
    sedimentSump = models.FloatField(_('Lengte zandvang'),default = 0)