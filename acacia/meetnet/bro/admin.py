# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.admin.decorators import register

from acacia.meetnet.models import Network

from .fields import CodeField
from .models import GroundwaterMonitoringWell, MonitoringTube, \
    Code, CodeSpace, RegistrationRequest, Defaults


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

    def get_form(self, request, obj=None, **kwargs):
        form = admin.ModelAdmin.get_form(self, request, obj=obj, **kwargs)
        form.base_fields['default_code'].queryset = obj.code_set.all()
        return form
    
@register(Code)
class CodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'codeSpace')    
    list_filter = ('codeSpace',)
    list_search = ('code','codeSpace')
    ordering = ('codeSpace','code')
    
@register(RegistrationRequest)
class RegisterAdmin(CodeFieldAdmin):
    def get_changeform_initial_data(self, request):
        data = CodeFieldAdmin.get_changeform_initial_data(self, request)
        try:
            network = Network.objects.first() 
            data['deliveryAccountableParty'] = network.bro.deliveryAccountableParty
        except:
            pass
        return data

@register(Defaults)
class DefaultsAdmin(admin.ModelAdmin):
    def get_changeform_initial_data(self, request):
        data = admin.ModelAdmin.get_changeform_initial_data(self, request)
        data['network'] = Network.objects.first()
        return data