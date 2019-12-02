# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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
