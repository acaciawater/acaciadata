# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from acacia.meetnet.models import Screen
from django.utils.translation import ugettext_lazy as _
from ..fields import CodeField, IndicationYesNoUnknownEnumeration
    
class MonitoringTube(models.Model):
    ''' Tube data for BRO '''
    screen = models.OneToOneField(Screen,on_delete=models.CASCADE,verbose_name=_('tube'), related_name='bro')

    tubeNumber = models.PositiveSmallIntegerField(default = 1)
    tubeType = CodeField(codeSpace='TubeType', verbose_name=_('Buistype'), default='standaardbuis')
    artesianWellCapPresent = IndicationYesNoUnknownEnumeration(verbose_name=_('ArtesianWellCapPresent'))
    sedimentSumpPresent = IndicationYesNoUnknownEnumeration(verbose_name=_('SedimentSumpPresent')) # True als diepte > onderkant filter
    numberOfGeoOhmCables = models.PositiveSmallIntegerField(verbose_name=_('NumberOfGeoOhmCables'), default = 0)
    tubeTopDiameter = models.FloatField(_('Diameter'))
    variableDiameter = models.BooleanField(_('Variabele diameter'),default=False)
    tubeStatus = CodeField(codeSpace='TubeStatus',verbose_name=_('Status'),default='gebruiksklaar')
    tubeTopPosition = models.FloatField(_('Bovenkant buis'))
    tubeTopPositioningMethod = CodeField(codeSpace='TubeTopPositioningMethod',verbose_name=_('Methode positiebepaling bovenkant buis'),default='onbekend')
    tubePackingMaterial = CodeField(codeSpace='TubePackingMaterial',verbose_name=_('Aanvul materiaal'),default='onbekend')
    tubeMaterial = CodeField(codeSpace='TubeMaterial',verbose_name=_('Buismateriaal'),default='pvc')
    screenLength = models.FloatField(_('Filterlengte'))
    sockMaterial = CodeField(codeSpace='SockMaterial',verbose_name=_('Kousmateriaal'),default='onbekend')
    plainTubePartLength = models.FloatField(_('Lengte stijgbuis'))
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
            self.plainTubePartLength = top + refpnt - maaiveld
        if not (depth is None or bottom is None):
            self.sedimentSump = depth - bottom
        
    @classmethod
    def create_for_screen(cls, screen):
        tube = MonitoringTube(screen=screen)
        tube.update()
        tube.save()
        
    class Meta:
        verbose_name = _('MonitoringTube')
        verbose_name_plural = _('MonitoringTubes')        