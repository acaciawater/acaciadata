# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from .models import CodeSpace

class CodeField(models.CharField):
    ''' BRO code implemented as CharField '''
    
    def __init__(self, *args, **kwargs):
        if 'max_length' not in kwargs:
            kwargs['max_length'] = 20
        self.codeSpace = kwargs.pop('codeSpace',None)
                
        if self.codeSpace:
            try:
                space = CodeSpace.objects.get(codeSpace__iexact=self.codeSpace)
                if 'default' not in kwargs and space.default_code:
                    kwargs['default'] = space.default_code.code
                # choices are set in admin.py
            except:
                pass
        models.CharField.__init__(self, *args, **kwargs)

class CodeFKField(models.ForeignKey):
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
            queryset = CodeSpace.objects.filter(codeSpace__iexact=self.codeSpace)
            if queryset.exists():
                instance = queryset.first()
                kwargs['default'] = instance.default_code.id
                kwargs['limit_choices_to'] = {'codeSpace': instance }
        except:
            pass
        models.ForeignKey.__init__(self,**kwargs)

class IndicationYesNoEnumeration(CodeField):
    def __init__(self,*args, **kwargs):
        return CodeField.__init__(self,codeSpace='IndicationYesNoEnumeration', **kwargs)
    
class IndicationYesNoUnknownEnumeration(CodeField):
    def __init__(self,*args, **kwargs):
        return CodeField.__init__(self,codeSpace='IndicationYesNoUnknownEnumeration', **kwargs)
