'''
Created on Jun 1, 2014

@author: theo
'''
from .models import Network, Well, Photo, Screen, Datalogger, LoggerDatasource
from acacia.data.models import Series
from django.conf import settings
from django.contrib import admin
from django.contrib.gis import admin as geo

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
    list_display=('serial', 'model', 'screen', 'baro', 'refpnt', 'depth', 'date')
    search_fields = ('serial', 'screen__well__name',)
    list_filter = ('screen__well', 'date')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'baro':
            kwargs['queryset'] = Series.objects.filter(parameter__datasource__name__startswith='Baro')
        return super(DataloggerAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
        
class LoggerDatasourceAdmin(admin.ModelAdmin):
    list_display=('logger', 'name', 'description', 'meetlocatie', 'last_download', 'filecount', 'parametercount', 'seriescount', 'start', 'stop', 'rows',)
    search_fields = ['name',]
    list_filter = ('meetlocatie','meetlocatie__projectlocatie','meetlocatie__projectlocatie__project',)
        
class ScreenAdmin(admin.ModelAdmin):
    actions = [actions.make_screencharts,]
    list_display = ('__unicode__', 'top', 'bottom', 'num_files', 'num_standen', 'start', 'stop')
    search_fields = ('well__name',)
    list_filter = ('well','well__network')
    
class WellAdmin(geo.OSMGeoAdmin):
    actions = [actions.make_wellcharts,]
    inlines = [PhotoInline, ]
    list_display = ('name','network','num_filters', 'num_photos', 'logger_names', 'straat', 'plaats')
    #list_editable = ('location',)
    #list_per_page = 4
    ordering = ('network', 'name',)
    list_filter = ('network', )
    save_as = True
    search_fields = ['name', 'nitg', 'plaats']
    list_select_related = True
    fieldsets = (
                 ('Algemeen', {'classes': ('grp-collapse', 'grp-open'),
                               'fields':('network', 'name', 'nitg', 'bro', 'maaiveld', 'refpnt', 'date', 'log')}),
                 ('Locatie', {'classes': ('grp-collapse', 'grp-open'),
                              'fields':(('straat', 'huisnummer'), ('postcode', 'plaats'),'location',)}),
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

admin.site.register(Well, WellAdmin)
admin.site.register(Screen, ScreenAdmin)
admin.site.register(Datalogger, DataloggerAdmin)
admin.site.register(LoggerDatasource, LoggerDatasourceAdmin)
admin.site.register(Photo,PhotoAdmin)
admin.site.register(Network)
