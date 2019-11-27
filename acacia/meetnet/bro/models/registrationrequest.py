# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from xml.etree.ElementTree import Element, SubElement

from django.db import models
from django.utils.translation import ugettext_lazy as _

from acacia.meetnet.bro.fields import CodeField
from acacia.meetnet.bro.validators import ChamberOfCommerceValidator


class RegistrationRequest(models.Model):
    requestReference = models.CharField(_('requestReference'),max_length=100)
    deliveryAccountableParty = models.CharField(_('deliveryAccountableParty'),max_length=8,validators=[ChamberOfCommerceValidator],help_text=_('KVK nummer van bronhouder'))
    qualityRegime = CodeField(codeSpace='qualityRegime',verbose_name=_('Kwaliteitsregime'))
#     broId = models.CharField(_('broid'),max_length=20)
    underPrivilege = models.NullBooleanField(_('Onder voorrecht'))
    
    def asxml(self):
        ''' Creates xml with BRO request '''
        request = Element('ns:registrationRequest',
        {
            'xmlns:ns':'http://www.broservices.nl/xsd/isgmw/1.1',
            'xmlns:ns1':'http://www.broservices.nl/xsd/brocommon/3.0',        
            'xmlns:ns2':'http://www.broservices.nl/xsd/gmwcommon/1.1',
            'xmlns:ns3':'http://www.opengis.net/gml/3.2'
        })
        SubElement(request, 'ns1:requestReference').text = self.requestReference
        SubElement(request, 'ns1:deliveryAccountableParty').text = self.deliveryAccountableParty
        SubElement(request, 'ns1:qualityRegime').text = self.qualityRegime
        return request