'''
Created on Jul 8, 2014

@author: theo
'''
import os
from django.utils.text import slugify
from .util import make_chart, recomp, createmeteo
from acacia.data.models import Series, Project, ProjectLocatie, MeetLocatie
 
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