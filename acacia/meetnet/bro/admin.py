# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from django.contrib.admin.decorators import register
from acacia.meetnet.bro.models import GroundwaterMonitoringWell, MonitoringTube,\
    Code

class GroundwaterMonitoringWellInline(admin.TabularInline):
    model = GroundwaterMonitoringWell

class MonitoringTubeInline(admin.TabularInline):
    model = MonitoringTube
    
@register(GroundwaterMonitoringWell)
class GroundwaterMonitoringWellAdmin(admin.ModelAdmin):
    pass

@register(MonitoringTube)
class MonitoringTubeAdmin(admin.ModelAdmin):
    pass

@register(Code)
class CodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'codeSpace', 'default_value')    
    list_filter = ('codeSpace','default_value')
    list_search = ('code','codeSpace')
    ordering = ('codeSpace','code')