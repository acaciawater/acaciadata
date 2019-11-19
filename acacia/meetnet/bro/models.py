# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your models here.

# This is an auto-generated Django model module created by ogrinspect.
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from acacia.meetnet.models import Well, Screen
from django.utils.translation import ugettext_lazy as _
from django.db.models.deletion import CASCADE

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
    codeSpace = models.CharField(_('codeSpace'),max_length=40)
    code = models.CharField(_('code'),max_length=40)

    def __unicode__(self):
        return self.code
    
    class Meta:
        unique_together = ('codeSpace', 'code')
        
def CodeField(codeSpace, displayName=None):
    return models.ForeignKey(Code,
                             on_delete=models.CASCADE,
                             related_name='+',
                             limit_choices_to={'codeSpace':codeSpace},
                             verbose_name=displayName or _(codeSpace))

# class RegistrationRequest(models.Model):
#     requestReference = models.CharField(_('requestReference'),max_length=100)
#     deliveryAccountableParty = models.CharField(_('deliveryAccountableParty'),max_length=8)
#     broId = models.CharField(_('broid'),max_length=20)
#     qualityRegime = CodeField('qualityRegime',_('Kwaliteitsregime'))
#     underPrivilege = models.NullBooleanField(_('Onder voorrecht'))        

class GroundwaterMonitoringWell(models.Model):
    ''' Well data for BRO '''
    well = models.OneToOneField(Well,on_delete=models.CASCADE,related_name='bro')

    deliveryContext = CodeField('deliveryContext',_('Kader aanlevering'))
    constructionStandard = CodeField('constructionStandard',_('Kwaliteitsnorm inrichting'))
    initialFunction = CodeField('initialFunction',_('Initiële functie'))
    #numberOfMonitoringTubes = well.screen_set.count()
    groundLevelStable = models.NullBooleanField(_('Maaiveld stabiel'),default='onbekend')
    wellStability = models.NullBooleanField(_('Putstabiliteit'), max_length=16,default='onbekend')
    #nitgCode = well.nitg
    #mapSheetCode = calculated from well.location
    #owner = well.owner
    maintenanceResponsibleParty = models.CharField(_('Onderhoudende instantie'),max_length=8,null=True,blank=True)
    wellHeadProtector = CodeField('wellHeadProtector',_('Beschermconstructie'))
    #wellConstructionDate = well.date
    #deliveredLocation = well.location
    #deliveredVerticalPosition = well.maaiveld

class MonitoringTube(models.Model):
    ''' additional screen data for BRO '''
    screen = models.OneToOneField(Screen,on_delete=models.CASCADE,related_name='bro')

    #tubeNumber = screen.nr
    tubeType = CodeField('tubeType', _('Buistype'))
    artesianWellCapPresent = models.NullBooleanField(_('Drukdop'))
    sedimentSumpPresent = models.NullBooleanField(_('Zandvang')) # True als diepte > onderkant filter
    #numberOfGeoOhmCables = 0
    #tubeTopDiameter = screen.diameter
    variableDiameter = models.BooleanField(_('Variabele diameter'),default=False)
    tubeStatus = CodeField('tubeStatus', ('Status'))
    #tubeTopPosition = screen.refpnt
    tubeTopPositioningMethod = CodeField('tubeTopPositioningMethod',_('Methode positiebepaling bovenkant buis'))
    tubePackingMaterial = CodeField('tubePackingMaterial',_('Aanvul materiaal'))
    #materialUsed = screen.material
    #screenLength = screen.top - screen.bottom
    sockMaterial = CodeField('sockMaterial',_('Kousmateriaal'))
    #plainTubePart = screen.refpnt - screen.well.maaiveld + screen.top
