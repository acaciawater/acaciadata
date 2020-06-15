# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.gis.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from acacia.meetnet.models import Well

from ..fields import CodeField, IndicationYesNoUnknownEnumeration
from ..validators import ChamberOfCommerceValidator
from .code import Code
from .codespace import CodeSpace
from .mapsheet import MapSheet
from django.contrib.auth.models import User

class GroundwaterMonitoringWell(models.Model):
    ''' Well data for BRO '''
    well = models.OneToOneField(Well,on_delete=models.CASCADE,verbose_name = _('well'), related_name='bro')
    objectIdAccountableParty=models.CharField(_('ObjectID'),max_length=100)
    deliveryContext = CodeField(codeSpace='DeliveryContext',verbose_name=_('Kader aanlevering'), default='publiekeTaak')
    constructionStandard = CodeField(codeSpace='ConstructionStandard',verbose_name=_('Kwaliteitsnorm inrichting'),default='onbekend')
    initialFunction = CodeField(codeSpace='InitialFunction',verbose_name=_('Initial function'),default='stand')
    numberOfMonitoringTubes = models.PositiveIntegerField(_('Number of monitoring tubes'), default=1)
    groundLevelStable = IndicationYesNoUnknownEnumeration(verbose_name=_('Ground level stable'))
    wellStability = IndicationYesNoUnknownEnumeration(verbose_name=_('WellStability'))
    nitgCode = models.CharField(_('NITG code'),max_length=8,blank=True,null=True)
    mapSheetCode = models.CharField(_('Mapsheet'),max_length=3,blank=True,null=True)
    owner = models.CharField(_('Owner'),max_length=8,validators=[ChamberOfCommerceValidator],help_text='KVK-nummer van de eigenaar')
    maintenanceResponsibleParty = models.CharField(_('Onderhoudende instantie'),max_length=8,validators=[ChamberOfCommerceValidator],null=True,blank=True)
    wellHeadProtector = CodeField(codeSpace='WellHeadProtector',verbose_name=_('Beschermconstructie'),default='onbekend')
    wellConstructionDate = models.DateField(null=True, blank=True)
    location = models.PointField(_('Coordinaten'))
    horizontalPositioningMethod = CodeField(codeSpace='HorizontalPositioningMethod',verbose_name=_('Methode locatiebepaling'), default='RTKGPS2tot5cm')
    groundLevelPosition = models.FloatField(_('Maaiveld'))
    groundLevelPositioningMethod = CodeField(codeSpace='GroundLevelPositioningMethod',verbose_name=_('Maaiveld positiebepaling'),default='RTKGPS0tot4cm')

    # Admin things
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name = _('user'))
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)
    
    def __unicode__(self):
        return str(self.well)
    
    def update(self, **kwargs):
        for attr in kwargs:
            if hasattr(self, attr):
                setattr(self, attr, kwargs[attr])
        
        try:
            bro = self.well.network.bro
            if not self.owner:
                self.owner = bro.owner
            if not self.maintenanceResponsibleParty:
                self.maintenanceResponsibleParty = bro.maintenanceResponsibleParty
        except ObjectDoesNotExist:
            # no defaults set for this network
            pass

        self.objectIdAccountableParty = self.well.name
        self.numberOfMonitoringTubes = self.well.screen_set.count()
        self.nitgCode = self.well.nitg
        sheets = MapSheet.from_location(self.well.location)
        if sheets.exists():
            self.mapSheetCode = sheets.first().blad
        self.wellConstructionDate = self.well.date
        self.location = self.well.location
        if self.well.maaiveld is not None:
            self.groundLevelPosition = self.well.maaiveld
            self.groundLevelPositioningMethod = CodeSpace.default('groundLevelPositioningMethod').code
        elif self.well.ahn is not None:
            self.groundLevelPosition = self.well.ahn
            self.groundLevelPositioningMethod = Code.objects.get(codeSpace__iexact='groundLevelPositioningMethod',code__iexact='AHN3')
        
        # update tubes as well
#         for s in self.well.screen_set.all():
#             try:
#                 s.bro.update(**kwargs)
#             except ObjectDoesNotExist:
#                 # auto create monitoringtube
#                 from acacia.meetnet.bro.models.monitoringtube import MonitoringTube
#                 MonitoringTube.create_for_screen(s, **kwargs)
                               
    @classmethod
    def create_for_well(cls, well, **kwargs):
        gmw = GroundwaterMonitoringWell(well=well, **kwargs)
        gmw.update()
        gmw.save()
        
    class Meta:
        verbose_name = _('GroundwaterMonitoringWell')
        verbose_name_plural = _('GroundwaterMonitoringWells')        