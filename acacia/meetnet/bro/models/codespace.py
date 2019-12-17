'''
Created on Nov 27, 2019

@author: theo
'''
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models

class CodeSpace(models.Model):
    ''' urn:bro:gmw:CodeSpace '''
    codeSpace = models.CharField(_('codeSpace'),max_length=40)
    description = models.CharField(_('Description'),max_length=40,blank=True,null=True)
    default_code = models.ForeignKey('Code', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('default code'))
    
    def __str__(self):
        return self.codeSpace

    def choices(self):
        return map(lambda c: (c,c), self.code_set.order_by('code').values_list('code',flat=True))
        
    @classmethod
    def default(cls,codeSpace):
        return cls.objects.get(codeSpace=codeSpace).default_code

    class Meta:
        verbose_name = _('Code space')
        verbose_name_plural = _('Code spaces')
