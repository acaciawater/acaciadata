# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from .models import CodeSpace

class CodeCharField(models.CharField):
    ''' BRO code implemented as CharField '''
    def __init__(self, *args, **kwargs):
        self.codeSpace = kwargs.pop('codeSpace',None)
        if 'max_length' not in kwargs:
            kwargs['max_length'] = 20
        if 'default' not in kwargs:
            kwargs['default'] = CodeSpace.objects.get(codeSpace=self.codeSpace).default_code.code
        super(CodeCharField,self).__init__(*args, **kwargs)

class CodeField(models.ForeignKey):
    ''' BRO code implemented as ForeignKey. 
    This is a bit hacky, because lambda functions (to set default) are not supported in migrations
    ''' 
    def __init__(self, *args, **kwargs):
        self.codeSpace = kwargs.pop('codeSpace',None)
        kwargs['to'] = 'bro.Code'
        kwargs['on_delete'] = models.CASCADE
        kwargs['related_name'] = '+'
#         kwargs['verbose_name'] = _(self.codeSpace) # does this work?
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
        super(CodeField,self).__init__(**kwargs)
