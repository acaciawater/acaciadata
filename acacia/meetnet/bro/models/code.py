'''
Created on Nov 27, 2019

@author: theo
'''
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models
from .codespace import CodeSpace
        
class Code(models.Model):
    ''' code from a urn:bro:gmw:CodeSpace '''
    codeSpace = models.ForeignKey(CodeSpace, on_delete=models.CASCADE)
    code = models.CharField(_('code'),max_length=40)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = _('Code')
        verbose_name_plural = _('Codes')
       
