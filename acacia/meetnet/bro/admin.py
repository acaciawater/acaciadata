# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from django.contrib.admin.decorators import register
from acacia.meetnet.bro.models import GroundwaterMonitoringWell, MonitoringTube,\
    Code, CodeSpace

from django.contrib.gis.db import models
from django import forms
from django.forms.models import ModelForm

class GroundwaterMonitoringWellInline(admin.TabularInline):
    model = GroundwaterMonitoringWell

class MonitoringTubeInline(admin.TabularInline):
    model = MonitoringTube
    
# class GroundwaterMonitoringWellForm(ModelForm):
#     model = GroundwaterMonitoringWell
#     deliveryContext = forms.ModelChoiceField(queryset=Code.objects.filter(codeSpace__codeSpace='deliveryContext'), initial=CodeSpace.objects.get(codeSpace='deliveryContext').default_code)
# 
#     def __init__(self,*args, **kwargs):
#         super(GroundwaterMonitoringWellForm,self).__init__(*args, **kwargs)
#         
@register(GroundwaterMonitoringWell)
class GroundwaterMonitoringWellAdmin(admin.ModelAdmin):
    #form = GroundwaterMonitoringWellForm
    formfield_overrides = {
        models.PointField:{'widget': forms.TextInput(attrs={'class': 'vTextField'})}
    }
@register(MonitoringTube)
class MonitoringTubeAdmin(admin.ModelAdmin):
    pass

@register(CodeSpace)
class CodeSpaceAdmin(admin.ModelAdmin):
    list_display = ('codeSpace','default_code')    
    list_filter = ('codeSpace',)
    ordering = ('codeSpace',)
    
@register(Code)
class CodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'codeSpace')    
    list_filter = ('codeSpace',)
    list_search = ('code','codeSpace')
    ordering = ('codeSpace','code')