'''
Created on Jul 8, 2014

@author: theo
'''
import os, sys, logging
from django.utils.text import slugify
from .util import make_chart, recomp, createmeteo
from acacia.data.models import Series, Project, ProjectLocatie, MeetLocatie
import nitg
from acacia.data import actions
import StringIO
logger = logging.getLogger(__name__)

def store_screens_nitg(queryset, zf):
    ''' store series as NITG format in zip file'''
    for screen in queryset:
        if screen.has_data():
            if screen.well.nitg:
                filename = '{}_{:03d}.nitg'.format(screen.well.nitg, screen.nr)
            else:
                filename = '{}_{:03d}.nitg'.format(screen.well.name, screen.nr)
            logger.debug('adding %s' % filename)
            io = StringIO.StringIO()
            nitg.write_header(io, source=screen.well.network.name)
            nitg.write_data(io, screen)
            zf.writestr(filename,io.getvalue())

def store_wells_nitg(queryset, zf):
    ''' store series as NITG format in zip file'''
    for well in queryset:
        if well.has_data():
            store_screens_nitg(well.screen_set.all(), zf)
            
def download_screen_nitg(modeladmin, request, queryset):
    actions.download_series_zip(modeladmin, request, queryset, store_screens_nitg)
download_screen_nitg.short_description='NITG Export'
    
def download_well_nitg(modeladmin, request, queryset):
    actions.download_series_zip(modeladmin, request, queryset, store_wells_nitg)
download_well_nitg.short_description='NITG Export'

def make_wellcharts(modeladmin, request, queryset):
    for w in queryset:
        if not w.has_data():
            continue
#        if w.chart.name is None or len(w.chart.name) == 0:
        w.chart.name = os.path.join(w.chart.field.upload_to, slugify(unicode(w)) +'.png')
        w.save()
        imagedir = os.path.dirname(w.chart.path)
        if not os.path.exists(imagedir):
            os.makedirs(imagedir)
        with open(w.chart.path,'wb') as f:
            f.write(make_chart(w))
        
make_wellcharts.short_description = "Grafieken vernieuwen van geselecteerde putten"
    
    
def make_screencharts(modeladmin, request, queryset):
    for s in queryset:
        if not s.has_data():
            continue
        if s.chart.name is None or len(s.chart.name) == 0:
            s.chart.name = os.path.join(s.chart.field.upload_to, slugify(unicode(s)) +'.png')
            s.save()
            imagedir = os.path.dirname(s.chart.path)
            if not os.path.exists(imagedir):
                os.makedirs(imagedir)
        with open(s.chart.path,'wb') as f:
            f.write(make_chart(s))
        
make_screencharts.short_description = "Grafieken vernieuwen van geselecteerde filters"

def recomp_screens(modeladmin, request, queryset):
    for screen in queryset:
        name = '%s COMP' % unicode(screen)
        series, created = Series.objects.get_or_create(name=name,user=request.user)
        recomp(screen, series)
recomp_screens.short_description = "Gecompenseerde tijdreeksen opnieuw aanmaken voor geselecteerde filters"
        
def recomp_wells(modeladmin, request, queryset):
    for well in queryset:
        recomp_screens(modeladmin,request,well.screen_set.all())
    make_wellcharts(modeladmin, request, queryset)
recomp_wells.short_description = "Gecompenseerde tijdreeksen opnieuw aanmaken voor geselecteerde putten"

def add_meteo_for_wells(modeladmin, request, queryset):
    for well in queryset:
        createmeteo(request,well)
add_meteo_for_wells.short_description = "Meteostations en tijdreeksen toevoegen voor geselecteerde putten"

def register_wells(modeladmin, request, queryset):
    from util import register_well
    for well in queryset:
        register_well(well)
register_wells.short_description = 'Registreer geselecteerde putten bij acaciadata.com'

def register_screens(modeladmin, request, queryset):
    from util import register_screen
    for screen in queryset:
        register_screen(screen)
register_screens.short_description = 'Registreer geselecteerde filters bij acaciadata.com'