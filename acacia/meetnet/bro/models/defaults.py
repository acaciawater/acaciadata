# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from django.db import models
from acacia.meetnet.bro.validators import ChamberOfCommerceValidator
from acacia.meetnet.models import Network
        
class Defaults(models.Model):
    ''' default CoC numbers for new registration requests (network specific)'''

    network = models.OneToOneField(Network, on_delete=models.CASCADE, related_name='bro', verbose_name=_('Network'))
    
    # RegistrationRequest
    deliveryAccountableParty = models.CharField(_('deliveryAccountableParty'), max_length=8, validators=[ChamberOfCommerceValidator],
                                                help_text=_('KVK nummer van de bronhouder'))

    # GMW_Construction
    owner = models.CharField(_('Owner'), max_length=8, validators=[ChamberOfCommerceValidator], help_text='KVK-nummer van de eigenaar')
    maintenanceResponsibleParty = models.CharField(_('Onderhoudende instantie'), max_length=8, validators=[ChamberOfCommerceValidator],
                                                   null=True, blank=True, help_text='KVK-nummer van de onderhoudende instantie')

    def __str__(self):
        return self.network.name

    class Meta:
        verbose_name = _('Defaults')
        verbose_name_plural = _('Defaults')
       
