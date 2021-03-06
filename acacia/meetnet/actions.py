'''
Created on Jul 8, 2014

@author: theo
'''
import os, logging
from django.utils.text import slugify
from .util import make_chart, recomp, createmeteo
from acacia.data.models import Series
import nitg
from acacia.data import actions
from acacia.ahn.models import AHN
from django.shortcuts import get_object_or_404

import StringIO
from acacia.meetnet.util import register_screen, register_well,\
    drift_correct_screen, set_well_address, moncorrect
from django.core.exceptions import ObjectDoesNotExist
from acacia.meetnet.models import LoggerStat, Handpeilingen
from django.contrib import messages
from django.http.response import HttpResponse
from django.conf import settings
logger = logging.getLogger(__name__)

def download_metadata(modeladmin, request, queryset):
    textbuffer = 'naam, nitg, filter, code, x, y, maaiveld, ahn, bovenkantbuis, bovenkantfilter, onderkantfilter, logger, ophangpunt, kabellengte\n'
    for w in queryset:
        for s in w.screen_set.all():
            for lp in s.loggerpos_set.all():
                textbuffer += ','.join([str(x) for x in [w.name, w.nitg, s.nr, unicode(s), w.location.x, w.location.y, w.maaiveld, w.ahn, s.refpnt, s.top, s.bottom, lp.logger, lp.refpnt, lp.depth]])
                textbuffer += '\n'
    resp = HttpResponse(textbuffer, content_type = "text/csv")
    resp['Content-Disposition'] = 'attachment; filename=meta.csv'
    return resp
download_metadata.short_description = 'Download metadata voor geselecteerde putten'
    
def address_from_osm(modeladmin, request, queryset):
    for well in queryset:
        if set_well_address(well):
            well.save()
address_from_osm.short_description = 'Bepaal adres met Openstreetmap API'        
            
def elevation_from_ahn(modeladmin, request, queryset):
    """ get elevation from AHN """
    ahn3 = get_object_or_404(AHN,name='AHN3 0.5m DTM')
    ahn2 = get_object_or_404(AHN,name='AHN2 0.5m geinterpoleerd')
    numok = 0
    numfail = 0
    for mp in queryset:
        p = mp.RD()
        x = p.x
        y = p.y
        try:
            ahn = ahn3.get_elevation(x,y)
            if not ahn:
                ahn = ahn2.get_elevation(x,y)
            if not ahn:
                numfail += 1
            else:
                numok += 1
                mp.ahn=ahn
                mp.save(update_fields=('ahn',))
        except Exception as e:
            numfail += 1
            #logger.exception('Fout bij maaiveld bepaling voor {}'.format(mp))
    if numfail:
        messages.warning(request, 'Voor {} putten is het niet gelukt om het AHN maaiveld op te vragen.'.format(numfail))
    if numok:
        messages.success(request, 'AHN maaiveld voor {} putten met succes bepaald.'.format(numok))
elevation_from_ahn.short_description = 'Bepaal maaiveldhoogte in NAP adhv AHN'        

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

def update_statistics(modeladmin, request, queryset):
    for lp in queryset:
        try:
            s = lp.loggerstat
        except ObjectDoesNotExist:
            s = LoggerStat.objects.create(loggerpos = lp)
        print lp
        s.update()
update_statistics.short_description = 'statistiek vernieuwen'

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

def drift_screens(modeladmin, request, queryset):
    for screen in queryset:
        drift_correct_screen(screen,request.user)
drift_screens.short_description = 'Filters corrigeren voor drift'

def drift_monfile(modeladmin, request, queryset):
    for monfile in queryset:
        moncorrect(monfile)
drift_monfile.short_description = 'Standen corrigeren voor drift'
        
def recomp_screens(modeladmin, request, queryset):
    for screen in queryset:
        register_screen(screen)
        series = screen.find_series()
        if not series:
            name = '%s COMP' % unicode(screen)
            series, created = Series.objects.update_or_create(name=name,defaults={
                'user':request.user,
                'mlocatie':screen.mloc,
                'timezone': 'Etc/GMT-1'
            })
        recomp(screen, series)
        series.validate(reset=True, accept=True, user=request.user)

    make_screencharts(modeladmin, request, queryset)
recomp_screens.short_description = "Gecompenseerde tijdreeksen opnieuw aanmaken voor geselecteerde filters"
        
def recomp_wells(modeladmin, request, queryset):
    for well in queryset:
        register_well(well)
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

def create_handpeilingen(modeladmin, request, queryset):
    num_created = 0
    for screen in queryset:
        hand, created = Handpeilingen.objects.get_or_create(screen=screen,defaults={
            'refpnt': 'bkb',
            'user': request.user,
            'mlocatie': screen.mloc,
            'name': '{} HAND'.format(screen),
            'unit': 'm',
            'type': 'scatter',
            'timezone': settings.TIME_ZONE
        })
        if created:
            num_created += 1
            screen.manual_levels = hand
            screen.save(update_fields=['manual_levels'])
    if num_created:
        messages.success(request, '{} reeksen toegevoegd.'.format(num_created))
    else:
        messages.warning(request, 'geen reeksen toegevoegd.')
            
create_handpeilingen.short_description = 'Maak tijdreeksen voor handpeilingen'