# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.gis.db import models
from acacia.meetnet.models import Well
from django.utils.translation import ugettext_lazy as _
from ..fields import CodeField
from ..validators import ChamberOfCommerceValidator
from .mapsheet import MapSheet
from .codespace import CodeSpace
from .code import Code

class GroundwaterMonitoringWell(models.Model):
    ''' Well data for BRO '''
    well = models.OneToOneField(Well,on_delete=models.CASCADE,related_name='bro')
    objectIdAccountableParty=models.CharField(_('ObjectID'),max_length=100)
    deliveryContext = CodeField(codeSpace='DeliveryContext',verbose_name=_('Kader aanlevering'), default='publiekeTaak')
    constructionStandard = CodeField(codeSpace='ConstructionStandard',verbose_name=_('Kwaliteitsnorm inrichting'),default='onbekend')
    initialFunction = CodeField(codeSpace='InitialFunction',verbose_name=_('Initial function'),default='stand')
    numberOfMonitoringTubes = models.PositiveIntegerField(_('Number of monitoring tubes'), default=1)
    groundLevelStable = models.NullBooleanField(_('Ground level stable'))
    wellStability = models.NullBooleanField(_('WellStability'), max_length=16)
    nitgCode = models.CharField(_('NITG code'),max_length=8,blank=True,null=True)
    mapSheetCode = models.CharField(_('Mapsheet'),max_length=3,blank=True,null=True)
    owner = models.CharField(_('Owner'),max_length=8,validators=[ChamberOfCommerceValidator],help_text='KVK-nummer van de eigenaar')
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
            self.groundLevelPositioningMethod = CodeSpace.objects.get(codespace__iexact='groundLevelPositioningMethod').default_code
        elif self.well.ahn is not None:
            self.deliveredVerticalPosition = self.well.ahn
            self.groundLevelPositioningMethod = Code.objects.get(codespace__iexact='groundLevelPositioningMethod',code__iexact='AHN3')
                            
    @classmethod
    def create_for_well(cls, well):
        gmw = GroundwaterMonitoringWell(well=well)
        gmw.update()
        gmw.save()
        
