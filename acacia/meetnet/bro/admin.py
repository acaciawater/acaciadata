# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.admin.decorators import register

from .models import GroundwaterMonitoringWell, MonitoringTube, \
    Code, CodeSpace, RegistrationRequest
from .fields import CodeField

class CodeFieldAdmin(admin.ModelAdmin):
    ''' Admin page with CodeFields '''
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        ''' adds choices to codefields '''
        if isinstance(db_field, CodeField):
            if hasattr(db_field, 'codeSpace') and not db_field.choices:
                db_field.choices = CodeSpace.objects.get(codeSpace__iexact=db_field.codeSpace).choices() 
        return admin.ModelAdmin.formfield_for_dbfield(self, db_field, request, **kwargs)

class GroundwaterMonitoringWellInline(admin.TabularInline):
    model = GroundwaterMonitoringWell

class MonitoringTubeInline(admin.TabularInline):
    model = MonitoringTube
    
@register(GroundwaterMonitoringWell)
class GroundwaterMonitoringWellAdmin(CodeFieldAdmin):
    exclude = ('objectIdAccountableParty',
               'numberOfMonitoringTubes',
               'nitgCode',
               'mapSheetCode',
               'wellConstructionDate',
               'location',
               'groundLevelPosition',
               'groundLevelPositioningMethod',
               ''
               )
    
    def save_model(self, request, obj, form, change):
        obj.update()
        admin.ModelAdmin.save_model(self, request, obj, form, change)
        
@register(MonitoringTube)
class MonitoringTubeAdmin(CodeFieldAdmin):
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
class RegisterAdmmin(CodeFieldAdmin):
    pass