# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from acacia.meetnet.bro.fields import CodeField,\
    IndicationYesNoUnknownEnumeration
from acacia.meetnet.bro.validators import ChamberOfCommerceValidator
from acacia.meetnet.bro.models import GroundwaterMonitoringWell
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

class RegistrationRequest(models.Model):
    requestReference = models.CharField(_('requestReference'),max_length=100,blank=True)
    deliveryAccountableParty = models.CharField(_('deliveryAccountableParty'),max_length=8,validators=[ChamberOfCommerceValidator],help_text=_('KVK nummer van bronhouder'))
    qualityRegime = CodeField(codeSpace='qualityRegime',verbose_name=_('Kwaliteitsregime'))
    underPrivilege = IndicationYesNoUnknownEnumeration(_('Onder voorrecht'))
    gmw = models.ForeignKey(GroundwaterMonitoringWell, on_delete=models.CASCADE, verbose_name=_('GroundwaterMonitoringWell'))
    
    # Admin things
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name = _('user'))
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)

    class Meta:
        verbose_name = _('RegistrationRequest')
        verbose_name_plural = _('RegistrationRequests')
        
    def __str__(self):
        return self.requestReference
    
    def _xml(self):
        ''' Returns xml Element with registration request for BRO '''
        from xml.etree.ElementTree import Element, SubElement
        
        xml = Element('ns:registrationRequest',
        {
            'xmlns:ns':'http://www.broservices.nl/xsd/isgmw/1.1',
            'xmlns:ns1':'http://www.broservices.nl/xsd/brocommon/3.0',        
            'xmlns:ns2':'http://www.broservices.nl/xsd/gmwcommon/1.1',
            'xmlns:ns3':'http://www.opengis.net/gml/3.2'
        })
        SubElement(xml, 'ns1:requestReference').text = self.requestReference # or update from well??
        SubElement(xml, 'ns1:deliveryAccountableParty').text = self.deliveryAccountableParty
        SubElement(xml, 'ns1:qualityRegime').text = self.qualityRegime
        SubElement(xml, 'ns1:underPrivilege').text = self.underPrivilege
        
        sourceDocument = SubElement(xml, 'ns:sourceDocument')
        construction = SubElement(sourceDocument, 'ns:GMW_Construction')
        
        # Check here is gmw is up-to-date?
        SubElement(construction, 'ns:objectIdAccountableParty').text = self.gmw.objectIdAccountableParty 
        SubElement(construction, 'ns:deliveryContext', codeSpace='urn:bro:gmw:DeliveryContext').text = self.gmw.deliveryContext
        SubElement(construction, 'ns:constructionStandard', codeSpace='urn:bro:gmw:ConstructionStandard').text = self.gmw.constructionStandard
        SubElement(construction, 'ns:initialFunction', codeSpace='urn:bro:gmw:InitialFunction').text = self.gmw.initialFunction
        SubElement(construction, 'ns:numberOfMonitoringTubes').text = str(self.gmw.numberOfMonitoringTubes)
        SubElement(construction, 'ns:groundLevelStable').text = self.gmw.groundLevelStable
        SubElement(construction, 'ns:wellStability', codeSpace='urn:bro:gmw:WellStability').text = self.gmw.wellStability
        if self.gmw.nitgCode:
            SubElement(construction, 'ns:nitgCode').text = self.gmw.nitgCode
        else:
            SubElement(construction, 'ns:mapSheetCode').text = self.gmw.mapSheetCode 
    
        SubElement(construction, 'ns:owner').text = self.gmw.owner
        SubElement(construction, 'ns:maintenanceResponsibleParty').text = self.gmw.maintenanceResponsibleParty
        SubElement(construction, 'ns:wellHeadProtector', codeSpace='urn:bro:gmw:WellHeadProtector').text = self.gmw.wellHeadProtector
        
        constructionDate = SubElement(construction, 'ns:wellConstructionDate')
        SubElement(constructionDate, 'ns1:date').text = '{:%Y-%m-%d}'.format(self.gmw.wellConstructionDate)
        deliveredLocation = SubElement(construction, 'ns:deliveredLocation')
        location = SubElement(deliveredLocation, 'ns2:location', {'ns3:id': 'id-426a1f26-360b-45e8-8c9d-469e6b33c7c3', 'srsName': 'urn:ogc:def:crs:EPSG::28992'})
        SubElement(location, 'ns3:pos').text = '{:.2f} {:.2f}'.format(self.gmw.location.x, self.gmw.location.y)
        SubElement(deliveredLocation, 'ns2:horizontalPositioningMethod', codeSpace='urn:bro:gmw:HorizontalPositioningMethod').text = self.gmw.horizontalPositioningMethod
        deliveredVerticalPosition = SubElement(construction, 'ns:deliveredVerticalPosition') 
        SubElement(deliveredVerticalPosition, 'ns2:localVerticalReferencePoint', codeSpace='urn:bro:gmw:LocalVerticalReferencePoint').text = 'NAP'
        SubElement(deliveredVerticalPosition, 'ns2:offset', uom='m').text = '0.00'
        SubElement(deliveredVerticalPosition, 'ns2:verticalDatum', codeSpace='urn:bro:gmw:VerticalDatum').text = 'NAP'
        SubElement(deliveredVerticalPosition, 'ns2:groundLevelPosition', uom="m").text = '{:.2f}'.format(self.gmw.groundLevelPosition)
        SubElement(deliveredVerticalPosition, 'ns2:groundLevelPositioningMethod', codeSpace='urn:bro:gmw:GroundLevelPositioningMethod').text = self.gmw.groundLevelPositioningMethod
        
        for screen in self.gmw.well.screen_set.order_by('nr'):
            monitoringTube = SubElement(construction, 'ns:monitoringTube')
            try:
                t = screen.bro
            except ObjectDoesNotExist:
                raise ValueError(_('No BRO data for screen %s') % screen)
            SubElement(monitoringTube, 'ns:tubeNumber').text = '{}'.format(t.tubeNumber)
            SubElement(monitoringTube, 'ns:tubeType', codeSpace="urn:bro:gmw:TubeType").text=t.tubeType
            SubElement(monitoringTube, 'ns:artesianWellCapPresent').text = t.artesianWellCapPresent
            SubElement(monitoringTube, 'ns:sedimentSumpPresent').text=t.sedimentSumpPresent
            SubElement(monitoringTube, 'ns:numberOfGeoOhmCables').text = '0'
            SubElement(monitoringTube, 'ns:tubeTopDiameter', uom="mm").text = '{:.0f}'.format(t.tubeTopDiameter)
            SubElement(monitoringTube, 'ns:variableDiameter').text=t.variableDiameter
            SubElement(monitoringTube, 'ns:tubeStatus', codeSpace="urn:bro:gmw:TubeStatus").text=t.tubeStatus
            SubElement(monitoringTube, 'ns:tubeTopPosition', uom="m").text = '{:.3f}'.format(t.tubeTopPosition)
            SubElement(monitoringTube, 'ns:tubeTopPositioningMethod', codeSpace="urn:bro:gmw:TubeTopPositioningMethod").text = t.tubeTopPositioningMethod
            materialsUsed = SubElement(monitoringTube, 'ns:materialUsed')
            SubElement(materialsUsed,'ns2:tubePackingMaterial', codeSpace="urn:bro:gmw:TubePackingMaterial").text=t.tubePackingMaterial
            SubElement(materialsUsed,'ns2:tubeMaterial',codeSpace="urn:bro:gmw:TubeMaterial").text=t.tubeMaterial
            SubElement(materialsUsed,'ns2:glue', codeSpace="urn:bro:gmw:Glue").text = 'geen' 
            screenElement = SubElement(monitoringTube, 'ns:screen')
            SubElement(screenElement,'ns:screenLength', uom="m").text = '{:.3f}'.format(t.screenLength)
            SubElement(screenElement,'ns:sockMaterial', codeSpace="urn:bro:gmw:SockMaterial").text=t.sockMaterial
            plainTubePart = SubElement(monitoringTube, 'ns:plainTubePart')
            SubElement(plainTubePart, 'ns2:plainTubePartLength', uom="m").text = '{:.3f}'.format(t.plainTubePartLength)
    
        return xml
    
    def as_xml(self):
        ''' return xml content for this request '''
        from xml.etree import ElementTree
        return ElementTree.tostring(self._xml(),encoding='utf-8') # no xml-declaration

    def update(self, **kwargs):
        for attr in kwargs:
            if hasattr(self, attr):
                setattr(self, attr, kwargs[attr])
                
        if not self.requestReference:
            self.requestReference = _('Registratieverzoek voor put %(well)s') % {'well': self.gmw.well.name}
        if not self.deliveryAccountableParty:
            try:
                self.deliveryAccountableParty = self.gmw.well.network.bro.deliveryAccountableParty
            except ObjectDoesNotExist:
                self.deliveryAccountableParty = self.gmw.owner 
        # also update gmw
        self.gmw.update(**kwargs)

    @classmethod
    def create_for_well(cls, well, **kwargs):
        ''' create a registration request for a well '''
        request = RegistrationRequest(**kwargs)
        try:
            request.gmw = well.bro
        except ObjectDoesNotExist:
            ''' create GMW_Construction document '''
            request.gmw = GroundwaterMonitoringWell.create_for_well(well, user=request.user)
        request.update()
        request.save()
        return request
        