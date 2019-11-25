# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your models here.

# This is an auto-generated Django model module created by ogrinspect.
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from acacia.meetnet.models import Well, Screen
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator

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

class CodeSpace(models.Model):
    ''' urn:bro:gmw:CodeSpace '''
    codeSpace = models.CharField(_('codeSpace'),max_length=40)
    description = models.CharField(_('Description'),max_length=40,blank=True,null=True)
    default_code = models.ForeignKey('Code', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('default code'))
    
    def __str__(self):
        return self.codeSpace

    def choices(self):
        return map(lambda c: (c,c), self.code_set.values_list('code',flat=True))
        
    class Meta:
        verbose_name = _('Code space')
        verbose_name_plural = _('Code spaces')
        
class Code(models.Model):
    ''' code from a urn:bro:gmw:CodeSpace '''
    codeSpace = models.ForeignKey(CodeSpace, on_delete=models.CASCADE)
    code = models.CharField(_('code'),max_length=40)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = _('Code')
        verbose_name_plural = _('Codes')
       
class CodeCharField(models.CharField):
    ''' BRO code implemented as CharField '''
    def __init__(self, *args, **kwargs):
        self.codeSpace = kwargs.pop('codeSpace',None)
        if 'max_length' not in kwargs:
            kwargs['max_length'] = 20
        if 'default' not in kwargs:
            kwargs['default'] = CodeSpace.objects.get(codeSpace=self.codeSpace).default_code.code
        super(CodeCharField,self).__init__(*args, **kwargs)

class CodeField(models.ForeignKey):
    ''' BRO code implemented as ForeignKey. 
    This is a bit hacky, because lambda functions (to set default) are not supported in migrations
    ''' 
    def __init__(self, *args, **kwargs):
        self.codeSpace = kwargs.pop('codeSpace',None)
        kwargs['to'] = 'bro.Code'
        kwargs['on_delete'] = models.CASCADE
        kwargs['related_name'] = '+'
        try:
            if 'default' in kwargs:
                kwargs.pop('default')
            queryset = CodeSpace.objects.filter(codeSpace=self.codeSpace)
            if queryset.exists():
                instance = queryset.first()
                kwargs['default'] = instance.default_code.id
                kwargs['limit_choices_to'] = {'codeSpace': instance }
        except:
            pass
        super(CodeField,self).__init__(**kwargs)
        
ChamberOfCommerceValidator = RegexValidator(regex=r'\d{8}',message=_('Illegal chamber of commerce number'))
        
# class RegistrationRequest(models.Model):
#     requestReference = models.CharField(_('requestReference'),max_length=100)
#     deliveryAccountableParty = models.CharField(_('deliveryAccountableParty'),max_length=8,validators=[ChamberOfCommerceValidator],help_text=_('KVK nummer van bronhouder'))
#     broId = models.CharField(_('broid'),max_length=20)
#     qualityRegime = CodeField(codeSpace='qualityRegime',verbose_name=_('Kwaliteitsregime'))
#     underPrivilege = models.NullBooleanField(_('Onder voorrecht'))
        
       
class GroundwaterMonitoringWell(models.Model):
    ''' Well data for BRO '''
    well = models.OneToOneField(Well,on_delete=models.CASCADE,related_name='bro')
    objectIdAccountableParty=models.CharField(_('ObjectID'),max_length=100)
    deliveryContext = CodeField(codeSpace='DeliveryContext',verbose_name=_('Kader aanlevering'), default='publiekeTaak')
    constructionStandard = CodeField(codeSpace='constructionStandard',verbose_name=_('Kwaliteitsnorm inrichting'),default='onbekend')
    initialFunction = CodeField(codeSpace='InitialFunction',verbose_name=_('Initiële functie'),default='stand')
    numberOfMonitoringTubes = models.PositiveIntegerField(_('Aantal monitoringbuizen'), default=1)
    groundLevelStable = models.NullBooleanField(_('Maaiveld stabiel'))
    wellStability = models.NullBooleanField(_('Putstabiliteit'), max_length=16)
    nitgCode = models.CharField(_('NITG code'),max_length=8,blank=True,null=True)
    mapSheetCode = models.CharField(_('Kaartblad'),max_length=3,blank=True,null=True)
    owner = models.CharField(_('Eigenaar'),max_length=8,validators=[ChamberOfCommerceValidator],help_text='KVK-nummer van de eigenaar')
    maintenanceResponsibleParty = models.CharField(_('Onderhoudende instantie'),max_length=8,validators=[ChamberOfCommerceValidator],null=True,blank=True)
    wellHeadProtector = CodeField(codeSpace='WellHeadProtector',verbose_name=_('Beschermconstructie'),default='onbekend')
    wellConstructionDate = models.DateField()
    deliveredLocation = models.PointField(_('Coordinaten'))
    horizontalPositioningMethod = CodeField(codeSpace='HorizontalPositioningMethod',verbose_name=_('Methode locatiebepaling'), default='RTKGPS2tot5cm')
    deliveredVerticalPosition = models.FloatField(_('Maaiveld'))
    groundLevelPositioningMethod = CodeField(codeSpace='GroundLevelPositioningMethod',verbose_name=_('Maaiveld positiebepaling'),default='RTKGPS0tot4cm')
    
    def __unicode__(self):
        return str(self.well)
    
    def update(self):
        self.numberOfMonitoringTubes = self.well.screen_set.count()
        self.nitgCode = self.well.nitg
        sheets = MapSheet.from_location(self.well.location)
        if sheets.exists():
            self.mapSheetCode = sheets.first().blad
        self.wellConstructionDate = self.well.date
        self.deliveredLocation = self.well.location
        if self.well.maaiveld is not None:
            self.deliveredVerticalPosition = self.well.maaiveld
            self.groundLevelPositioningMethod = Code.default('groundLevelPositioningMethod')
        elif self.well.ahn is not None:
            self.deliveredVerticalPosition = self.well.ahn
            self.groundLevelPositioningMethod = Code.get('groundLevelPositioningMethod','AHN3')
                            
    @classmethod
    def create_for_well(cls, well):
        gmw = GroundwaterMonitoringWell(well=well)
        gmw.update()
        gmw.save()
        
class MonitoringTube(models.Model):
    ''' Screen data for BRO '''
    screen = models.OneToOneField(Screen,on_delete=models.CASCADE,related_name='bro')

    tubeNumber = models.PositiveSmallIntegerField(default = 1)
    tubeType = CodeField(codeSpace='TubeType', verbose_name=_('Buistype'), default='standaardbuis')
    artesianWellCapPresent = models.NullBooleanField(_('Drukdop'))
    sedimentSumpPresent = models.NullBooleanField(_('Zandvang')) # True als diepte > onderkant filter
    numberOfGeoOhmCables = models.PositiveSmallIntegerField(default = 0)
    tubeTopDiameter = models.FloatField(_('Diameter'))
    variableDiameter = models.BooleanField(_('Variabele diameter'),default=False)
    tubeStatus = CodeField(codeSpace='TubeStatus',verbose_name=_('Status'),default='gebruiksklaar')
    tubeTopPosition = models.FloatField(_('Bovenkant buis'))
    tubeTopPositioningMethod = CodeField(codeSpace='TubeTopPositioningMethod',verbose_name=_('Methode positiebepaling bovenkant buis'),default='onbekend')
    tubePackingMaterial = CodeField(codeSpace='TubePackingMaterial',verbose_name=_('Aanvul materiaal'),default='onbekend')
    tubeMaterial = CodeField(codeSpace='TubeMaterial',verbose_name=_('Buismateriaal'),default='pvc')
    screenLength = models.FloatField(_('Filterlengte'))
    sockMaterial = CodeField(codeSpace='SockMaterial',verbose_name=_('Kousmateriaal'),default='onbekend')
    plainTubePart = models.FloatField(_('Lengte stijgbuis'))
    sedimentSump = models.FloatField(_('Lengte zandvang'),default = 0)
    
    def __unicode__(self):
        return str(self.screen)
    
    def update(self):
        self.tubeNumber = self.screen.nr
        self.tubeTopDiameter = self.screen.diameter
        self.tubeTopPosition = self.screen.refpnt
        
        top = self.screen.top
        bottom = self.screen.bottom
        depth = self.screen.depth
        refpnt = self.screen.refpnt
        maaiveld = self.screen.well.maaiveld

        if not (top is None or bottom is None):
            self.screenLength = top - bottom
        if not (top is None or refpnt is None or maaiveld is None):
            self.plainTubePart = top + refpnt - maaiveld
        if not (depth is None or bottom is None):
            self.sedimentSump = depth - bottom
        
    @classmethod
    def create_for_screen(cls, screen):
        tube = MonitoringTube(screen=screen)
        tube.update()
        tube.save()
   