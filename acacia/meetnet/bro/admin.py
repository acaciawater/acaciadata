# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.contrib import admin
from django.contrib.admin.decorators import register
from django.contrib.gis.db import models

from .models import GroundwaterMonitoringWell, MonitoringTube, \
    Code, CodeSpace, RegistrationRequest


class GroundwaterMonitoringWellInline(admin.TabularInline):
    model = GroundwaterMonitoringWell

class MonitoringTubeInline(admin.TabularInline):
    model = MonitoringTube
    
@register(GroundwaterMonitoringWell)
class GroundwaterMonitoringWellAdmin(admin.ModelAdmin):
    exclude = ('objectIdAccountableParty',
               'numberOfMonitoringTubes',
               'nitgCode',
               'mapSheetCode',
               'wellConstructionDate',
               'location',
               'deliveredVerticalPosition',
               'groundLevelPositioningMethod',
               ''
               )
    
    def save_model(self, request, obj, form, change):
        obj.update()
        admin.ModelAdmin.save_model(self, request, obj, form, change)
        
@register(MonitoringTube)
class MonitoringTubeAdmin(admin.ModelAdmin):
    exclude = ('tubeNumber',
               'tubeTopDiameter',
               'tubeTopPosition',
               'screenLength',
               'plainTubePartLength',
               'sedimentSump'
               )
    
    def save_model(self, request, obj, form, change):
        obj.update()
        admin.ModelAdmin.save_model(self, request, obj, form, change)

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
    
@register(RegistrationRequest)
class RegisterAdmmin(admin.ModelAdmin):
    pass