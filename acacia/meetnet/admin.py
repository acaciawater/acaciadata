'''
Created on Jun 1, 2014

@author: theo
'''
from .models import Network, Well, Photo, Screen, Datalogger, LoggerPos, LoggerDatasource, MonFile, Channel, ManualSeries
from acacia.data.admin import DatasourceAdmin, SourceFileAdmin, SeriesAdmin
from acacia.data.models import DataPoint
from django.conf import settings
from django.contrib import admin

USE_GOOGLE_TERRAIN_TILES = False

from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe

import actions

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

class DataloggerAdmin(admin.ModelAdmin):
    list_display=('serial', 'model')
    search_fields = ('serial',)
    list_filter = ('model',)

class LoggerPosAdmin(admin.ModelAdmin):
    model = LoggerPos
    list_display = ('logger', 'screen', 'start_date', 'end_date', 'refpnt', 'depth', 'baro', 'remarks')
    search_fields = ('logger__serial','screen__well__name')
    
class LoggerInline(admin.TabularInline):
    model = LoggerPos
    
class LoggerDatasourceAdmin(DatasourceAdmin):
    pass

#     def __init__(self, *args, **kwargs):
#         super(LoggerDatasourceAdmin,self).__init__(*args, **kwargs)
#         self.list_display = self.list_display[:3] + ( 'logger', ) + self.list_display[3:] 
#         self.search_fields = ['logger'].extend(self.search_fields)
#         dic = self.fieldsets[0][1]
#         fields = ('name', 'logger') + dic['fields'][1:]
#         self.fieldsets[0][1]['fields'] = fields

class DataPointInline(admin.TabularInline):
    model = DataPoint
    
class ManualSeriesAdmin(SeriesAdmin):
    model = ManualSeries
    inlines = [DataPointInline,]
    
class ChannelInline(admin.TabularInline):
    model = Channel

class ChannelAdmin(admin.ModelAdmin):
    list_display = ('identification', 'monfile', 'number', 'range', 'range_unit')
    
class MonFileAdmin(SourceFileAdmin):
    model = MonFile
    inlines = [ChannelInline,]
    list_display = ('name','datasource', 'source', 'serial_number', 'status', 'instrument_type', 'location', 'num_channels', 'num_points', 'start_date', 'end_date', 'uploaded',)
    list_filter = ('serial_number', 'datasource', 'datasource__meetlocatie', 'datasource__meetlocatie__projectlocatie__project', 'uploaded',)
    search_fields = ['name','file__name','serial_number']
    fields = None
    fieldsets = (
                 ('Algemeen', {'classes': ('grp-collapse', 'grp-open'),
                              'fields':('name', 'datasource', 'file', 'source')}),
                 ('Monfile', {'classes': ('grp-collapse', 'grp-closed'),
                               'fields':('company', 'compstat', 'date', 'monfilename', 'createdby', 'instrument_type', 'status',
                                         'serial_number','instrument_number','location','sample_period','sample_method','start_date','end_date', 'num_channels', 'num_points')}),
                )

class ScreenInline(admin.TabularInline):
    model = Screen
    extra = 0
        
class ScreenAdmin(admin.ModelAdmin):
    actions = [actions.make_screencharts,actions.recomp_screens]
    list_display = ('__unicode__', 'refpnt', 'top', 'bottom', 'num_files', 'num_standen', 'start', 'stop')
    search_fields = ('well__name', 'well__nitg')
    list_filter = ('well','well__network')

from django.contrib.gis.db import models
from django import forms
    
#class WellAdmin(geo.OSMGeoAdmin):
class WellAdmin(admin.ModelAdmin):
    formfield_overrides = {models.PointField:{'widget': forms.TextInput(attrs={'size': '100'})}}
    actions = [actions.make_wellcharts,actions.recomp_wells]
    inlines = [ ScreenInline, PhotoInline]
    list_display = ('name','nitg','network','maaiveld', 'num_filters', 'num_photos', 'straat', 'plaats')
    #list_editable = ('location',)
    #list_per_page = 4
    ordering = ('network', 'name',)
    list_filter = ('network', )
    save_as = True
    search_fields = ['name', 'nitg', 'plaats']
    list_select_related = True
    fieldsets = (
                 ('Algemeen', {'classes': ('grp-collapse', 'grp-open'),
                               'fields':('network', 'name', 'nitg', 'bro', 'maaiveld', 'date', 'log')}),
                 ('Locatie', {'classes': ('grp-collapse', 'grp-closed'),
                              'fields':(('straat', 'huisnummer'), ('postcode', 'plaats'),('location','g'),'description')}),
                )
    if USE_GOOGLE_TERRAIN_TILES:
        map_template = 'gis/admin/google.html'
        extra_js = ['http://openstreetmap.org/openlayers/OpenStreetMap.js', 'http://maps.google.com/maps?file=api&amp;v=2&amp;key=%s' % settings.GOOGLE_MAPS_API_KEY]
    else:
        pass # defaults to OSMGeoAdmin presets of OpenStreetMap tiles

    # Default GeoDjango OpenLayers map options
    # Uncomment and modify as desired
    # To learn more about this jargon visit:
    # www.openlayers.org
   
    #default_lon = 0
    #default_lat = 0
    default_zoom = 12
    #display_wkt = False
    #display_srid = False
    #extra_js = []
    #num_zoom = 18
    #max_zoom = False
    #min_zoom = False
    #units = False
    #max_resolution = False
    #max_extent = False
    #modifiable = True
    #mouse_position = True
    #scale_text = True
    #layerswitcher = True
    scrollable = False
    #admin_media_prefix = settings.ADMIN_MEDIA_PREFIX
    map_width = 400
    map_height = 325
    #map_srid = 4326
    #map_template = 'gis/admin/openlayers.html'
    #openlayers_url = 'http://openlayers.org/api/2.6/OpenLayers.js'
    #wms_url = 'http://labs.metacarta.com/wms/vmap0'
    #wms_layer = 'basic'
    #wms_name = 'OpenLayers WMS'
    #debug = False
    #widget = OpenLayersWidget

admin.site.register(Network)
admin.site.register(Well, WellAdmin)
admin.site.register(Screen, ScreenAdmin)
admin.site.register(Photo,PhotoAdmin)

admin.site.register(Datalogger, DataloggerAdmin)
admin.site.register(LoggerPos, LoggerPosAdmin)
admin.site.register(LoggerDatasource, LoggerDatasourceAdmin)
admin.site.register(MonFile,MonFileAdmin)
admin.site.register(Channel, ChannelAdmin)
admin.site.register(ManualSeries,ManualSeriesAdmin)

