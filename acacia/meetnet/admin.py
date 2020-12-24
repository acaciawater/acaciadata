'''
Created on Jun 1, 2014

@author: theo
'''
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.decorators import register
from django.contrib.admin.widgets import AdminFileWidget
from django.contrib.gis.db import models
from django.forms.widgets import Select
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from acacia.data.admin import DatasourceAdmin, SourceFileAdmin, DataPointInline, SeriesForm
from acacia.meetnet.actions import update_statistics, update_sourcefiles,\
    recomp_logpos
from acacia.meetnet.models import Handpeilingen
from acacia.meetnet.models import MeteoData
import actions

from .models import Network, Well, Photo, Screen, Datalogger, LoggerPos, LoggerDatasource, MonFile, Channel
from acacia.data.models import SourceFile

USE_GOOGLE_TERRAIN_TILES = False

class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None):
        output = []
        if value and getattr(value, "url", None):
            image_url = value.url
            file_name=str(value)
            output.append(u' <a href="%s" target="_blank"><img src="%s" alt="%s" height="256px"/></a>' % (image_url, image_url, file_name))
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))
    
class PhotoInline(admin.TabularInline):
    model = Photo
    fields = ('photo',)
    extra = 0
    classes = ('grp-collapse', 'grp-closed',)
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'photo':
            kwargs.pop('request')
            kwargs['widget'] = AdminImageWidget
            return db_field.formfield(**kwargs)
        return super(PhotoInline,self).formfield_for_dbfield(db_field, **kwargs)

@register(Photo)        
class PhotoAdmin(admin.ModelAdmin):
    list_display=('well', 'thumb', )
    search_fields = ['well__name', ]
    list_filter = ('well',)
    list_select_related = True

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'photo':
            kwargs.pop('request')
            kwargs['widget'] = AdminImageWidget
            return db_field.formfield(**kwargs)
        return super(PhotoAdmin,self).formfield_for_dbfield(db_field, **kwargs)

@register(Datalogger)
class DataloggerAdmin(admin.ModelAdmin):
    list_display=('serial', 'model')
    search_fields = ('serial',)
    list_filter = ('model',)

class MonFileInline(admin.TabularInline):
    model = MonFile
    classes = ['collapse']
    fields = ('name','file','rows', 'cols','start','stop')
    extra = 0
    ordering = ('start',)

class SourceFileInline(admin.TabularInline):
    model = LoggerPos.files.through
    classes = ['collapse']
    max_num = 20
#     fields = ('name','file','rows', 'cols','start','stop')
    extra = 0
#     ordering = ('-start',)

@register(LoggerPos)
class LoggerPosAdmin(admin.ModelAdmin):
    actions = [update_statistics, update_sourcefiles, recomp_logpos]
    list_display = ('logger', 'screen', 'start_date', 'end_date', 'refpnt', 'depth', 'num_files', 'remarks')
    list_filter = ('screen__well', 'screen',)
    search_fields = ('logger__serial','screen__well__name')
    exclude = ('files',)
#     inlines = [SourceFileInline]
    
class LoggerInline(admin.TabularInline):
    model = LoggerPos
    extra = 0
    exclude = ('description','files','remarks')
    classes = ('grp-collapse', 'grp-closed',)
    
@register(LoggerDatasource)
class LoggerDatasourceAdmin(DatasourceAdmin):
    fieldsets = (
                 ('Algemeen', {'fields': (('name', 'logger'), 'description', 'timezone', 'meetlocatie','locations'),
                               'classes': ('grp-collapse grp-open',),
                               }),
                 ('Bronnen', {'fields': (('generator', 'autoupdate'), 'url',('username', 'password',), 'config',),
                               'classes': ('grp-collapse grp-closed',),
                              }),
    )
    search_fields = ['name','meetlocatie__name']

#     def __init__(self, *args, **kwargs):
#         super(LoggerDatasourceAdmin,self).__init__(*args, **kwargs)
#         self.list_display = self.list_display[:3] + ( 'logger', ) + self.list_display[3:] 
#         self.search_fields = ['logger'].extend(self.search_fields)
#         dic = self.fieldsets[0][1]
#         fields = ('name', 'logger') + dic['fields'][1:]
#         self.fieldsets[0][1]['fields'] = fields

class ChannelInline(admin.TabularInline):
    model = Channel

class ChannelAdmin(admin.ModelAdmin):
    list_display = ('identification', 'monfile', 'number', 'range', 'range_unit')

@register(MonFile)    
class MonFileAdmin(SourceFileAdmin):
    inlines = [ChannelInline,]
    actions = [actions.drift_monfile]
    list_display = ('name','datasource', 'source', 'serial_number', 'status', 'instrument_type', 'location', 'num_channels', 'num_points', 'start_date', 'end_date', 'uploaded',)
    list_filter = ('serial_number', 'datasource', 'datasource__meetlocatie', 'datasource__meetlocatie__projectlocatie__project', 'uploaded',)
    search_fields = ['name','serial_number']
    fields = None
    fieldsets = (
                 ('Algemeen', {'classes': ('grp-collapse', 'grp-open'),
                              'fields':('name', 'datasource', 'file', 'source')}),
                 ('Monfile', {'classes': ('grp-collapse', 'grp-closed'),
                               'fields':('company', 'compstat', 'date', 'monfilename', 'createdby', 'instrument_type', 'status',
                                         'serial_number','instrument_number','location','sample_period','sample_method','start_date','end_date', 'num_channels', 'num_points')}),
                )

class MeteoInline(admin.StackedInline):
    model = MeteoData
    extra = 0
    classes = ('grp-collapse', )
        
class ScreenInline(admin.TabularInline):
    model = Screen
    extra = 0
    classes = ('grp-collapse', 'grp-closed',)
        
@register(Screen)
class ScreenAdmin(admin.ModelAdmin):
    actions = [actions.make_screencharts,
               actions.recomp_screens,
               actions.update_screens,
               actions.drift_screens,
               actions.register_screens,
               actions.download_screen_nitg,
               actions.create_handpeilingen,
               actions.clip_data]
    list_display = ('__unicode__', 'group', 'refpnt', 'top', 'bottom', 'aquifer', 'num_files', 'num_standen', 'start', 'stop', 'manual_levels')
    search_fields = ('well__name', 'well__nitg')
    list_filter = ('well','well__network','aquifer', 'group')
    inlines = [LoggerInline]
    ordering = ()
    
    def get_queryset(self, request):
        ''' override to perform custom sorting '''
        queryset = admin.ModelAdmin.get_queryset(self, request)
        # assume there is only one network. 
        key = Network.objects.first().display_name
        return queryset.order_by('well__'+key)

    def get_actions(self, request):
        ''' add bro actions dynamically, to avoid circular refs '''
        actions = admin.ModelAdmin.get_actions(self, request)
        if 'acacia.meetnet.bro' in settings.INSTALLED_APPS:
            from acacia.meetnet.bro.actions import add_bro_for_screens
            func,name,desc = self.get_action(add_bro_for_screens)
            actions[name]=(func,name,desc)
        return actions
    
    def get_form(self, request, obj=None, **kwargs):
        form = admin.ModelAdmin.get_form(self, request, obj=obj, **kwargs)
        form.base_fields['logger_levels'].queryset = obj.mloc.series_set.order_by('name')
        form.base_fields['manual_levels'].queryset = obj.mloc.series_set.order_by('name')
        return form
        
#     def get_inline_instances(self, request, obj=None):
#         instances = ModelAdmin.get_inline_instances(self, request, obj)
#         if hasattr(obj,'bro'):
#             # add bro inline
#             from acacia.meetnet.bro.admin import MonitoringTubeInline
#             instances.append(MonitoringTubeInline(self.model,self.admin_site))
#         return instances
        
#class WellAdmin(geo.OSMGeoAdmin):
@register(Well)
class WellAdmin(admin.ModelAdmin):
    formfield_overrides = {models.PointField:{'widget': forms.TextInput(attrs={'size': '100'})}}
    actions = [actions.make_wellcharts,
               actions.recomp_wells,
               actions.update_wells,
               actions.add_meteo_for_wells,
               actions.register_wells,
               actions.download_metadata,
               actions.download_well_nitg,
               actions.elevation_from_ahn,
               actions.address_from_location]

    inlines = [ScreenInline, MeteoInline, PhotoInline ]
    list_display = ('name','nitg','network','owner','maaiveld', 'ahn', 'num_filters', 'num_photos', 'straat', 'plaats')
    #list_editable = ('location',)
    #list_per_page = 4
#     ordering = ('nitg',)
    list_filter = ('network', 'owner','plaats')
    save_as = True
    search_fields = ['name', 'nitg', 'plaats']
    list_select_related = True
    fieldsets = (
                 ('Algemeen', {'classes': ('grp-collapse', 'grp-open'),
                               'fields':('network', 'name', 'nitg', 'broid', 'maaiveld', 'date', 'log', 'chart')}),
                 ('Locatie', {'classes': ('grp-collapse', 'grp-closed'),
                              'fields':(('straat', 'huisnummer'), ('postcode', 'plaats'),('location','g'),'description')}),
                )
    if USE_GOOGLE_TERRAIN_TILES:
        map_template = 'gis/admin/google.html'
        extra_js = ['http://openstreetmap.org/openlayers/OpenStreetMap.js', 'http://maps.google.com/maps?file=api&amp;v=2&amp;key=%s' % settings.GOOGLE_MAPS_API_KEY]
    else:
        pass # defaults to OSMGeoAdmin presets of OpenStreetMap tiles

    default_zoom = 12
    scrollable = False
    map_width = 400
    map_height = 325

    def get_actions(self, request):
        ''' add bro actions dynamically, to avoid circular refs '''
        actions = admin.ModelAdmin.get_actions(self, request)
        if 'acacia.meetnet.bro' in settings.INSTALLED_APPS:
            from acacia.meetnet.bro.actions import add_bro_for_wells
            func,name,desc = self.get_action(add_bro_for_wells)
            actions[name]=(func,name,desc)
        return actions

#     def get_inline_instances(self, request, obj=None):
#         instances = ModelAdmin.get_inline_instances(self, request, obj)
#         if hasattr(obj,'bro'):
#             # add bro inline
#             from acacia.meetnet.bro.admin import GroundwaterMonitoringWellInline
#             instances.append(GroundwaterMonitoringWellInline(self.model,self.admin_site))
#         return instances
     
@register(MeteoData)
class MeteoDataAdmin(admin.ModelAdmin):
    list_display = ('well','baro')
    search_fields = ('well__nitg','baro__name')
    list_filter = ('well','baro','neerslag','verdamping','temperatuur')

class HandForm(SeriesForm):
    bkb = forms.FloatField(label=_('Bovenkant buis'), required=False)

    class Media:
        js = ('/static/grappelli/jquery/jquery.min.js', 'js/handform.js',)

    class Meta:
        widgets = {'unit': Select(choices=(('cm','centimeter'),('m','meter')))}
                
    def __init__(self,*args,**kwargs):
        super(HandForm,self).__init__(*args,**kwargs)
        if self.instance and self.instance.pk:
            self.initial['bkb'] = self.instance.screen.refpnt
            self.fields['bkb'].widget.attrs['readonly'] = True
        
    def clean(self):
        cleaned_data = super(HandForm,self).clean()
        screen = cleaned_data['screen']
        cleaned_data['mlocatie'] = screen.mloc
        cleaned_data['name'] = '{}-HAND'.format(screen)
        return cleaned_data

@register(Handpeilingen)    
class HandpeilingenAdmin(admin.ModelAdmin):
    form = HandForm
    actions = []
    list_display = ('screen', 'unit', 'refpnt', 'timezone', 'aantal', 'van', 'tot', 'minimum', 'maximum', 'gemiddelde')
    list_filter = ('screen',)
    exclude = ('name', 'user','parameter','scale','offset')
    inlines = [DataPointInline,]
    search_fields = ['screen', 'name',]
    fields = ('screen','description', 'timezone', ('bkb', 'refpnt','unit'))
    fieldsets = ()

    def get_changeform_initial_data(self, request):
        return {'type': 'scatter','user': request.user, 'unit': 'm', 'timezone': settings.TIME_ZONE, 'scale': 1, 'offset': 0}

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()
        obj.getproperties().delete() # will be updated in due time

@register(Network)
class NetworkAdmin(admin.ModelAdmin):
    fields = ('name',('display_name','login_required'),('homepage','logo'),'bound',('last_round','next_round'))
