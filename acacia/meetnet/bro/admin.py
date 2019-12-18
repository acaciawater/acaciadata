# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.admin.decorators import register

from acacia.meetnet.models import Network, Well, Screen

from .fields import CodeField
from .models import GroundwaterMonitoringWell, MonitoringTube, \
    Code, CodeSpace, RegistrationRequest, Defaults
from django.core.exceptions import ObjectDoesNotExist
from acacia.meetnet.bro.actions import update_gmw, update_tube


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
    list_display = ('__str__', 'user', 'modified')
    list_filter = ('user', 'modified')
    actions = [update_gmw]
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'well':
            kwargs['queryset'] = Well.objects.order_by('name')
        return CodeFieldAdmin.formfield_for_foreignkey(self, db_field, request, **kwargs)
    
    def get_form(self, request, obj=None, **kwargs):
        form = CodeFieldAdmin.get_form(self, request, obj=obj, **kwargs)
        return form
    
    def get_changeform_initial_data(self, request):
        data = admin.ModelAdmin.get_changeform_initial_data(self, request)
        network = Network.objects.first()
        data['network'] = network
        try:
            bro = network.bro
            data['owner'] = bro.owner 
            data['maintenanceResponsibleParty'] = bro.maintenanceResponsibleParty
        except ObjectDoesNotExist:
            pass
        return data
    
    def save_model(self, request, obj, form, change):
        obj.update(user=request.user)
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
    list_display = ('__str__', 'user', 'modified')
    list_filter = ('user', 'modified')
    actions = [update_tube]
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'screen':
            kwargs['queryset'] = Screen.objects.order_by('well__name','nr')
        return CodeFieldAdmin.formfield_for_foreignkey(self, db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.update(user=request.user)
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
    search_fields = ('code','codeSpace')
    ordering = ('codeSpace','code')
    
@register(RegistrationRequest)
class RegistrationRequestAdmin(CodeFieldAdmin):
    list_display = ('__str__', 'deliveryAccountableParty', 'user', 'modified' )
    list_filter = ('gmw__well','gmw__owner', 'user', 'modified')
    search_fields = ('requestReference','gmw__well')
    
    def get_changeform_initial_data(self, request):
        data = CodeFieldAdmin.get_changeform_initial_data(self, request)
        try:
            network = Network.objects.first() 
            data['deliveryAccountableParty'] = network.bro.deliveryAccountableParty
        except ObjectDoesNotExist:
            pass
        return data

@register(Defaults)
class DefaultsAdmin(admin.ModelAdmin):
    def get_changeform_initial_data(self, request):
        data = admin.ModelAdmin.get_changeform_initial_data(self, request)
        data['network'] = Network.objects.first()
        return data