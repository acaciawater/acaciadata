from .shortcuts import meteo2locatie
from .models import Chart, Series, Grid, ManualSeries

import logging, re
logger = logging.getLogger(__name__)

def sourcefile_dimensions(modeladmin, request, queryset):
    '''sourcefile doorlezen en eigenschappen updaten (start, stop, rows etc)'''
    for sf in queryset:
        #sf.get_dimensions()
        sf.save() # pre-save signal calls get_dimensions
sourcefile_dimensions.short_description='Geselecteerde bronbestanden doorlezen en eigenschappen actualiseren'

def meetlocatie_aanmaken(modeladmin, request, queryset):
    '''standaard meetlocatie aanmaken op zelfde locatie als projectlocatie '''
    for p in queryset:
        p.meetlocatie_set.create(name=p.name,location=p.location, description=p.description)
meetlocatie_aanmaken.short_description = 'Standaard meetlocatie aanmaken voor geselecteerde projectlocaties'
        
def meteo_toevoegen(modeladmin, request, queryset):
    for loc in queryset:
        meteo2locatie(loc,user=request.user)
meteo_toevoegen.short_description = "Meteostation, neerslagstation en regenradar toevoegen"

def upload_datasource(modeladmin, request, queryset):
    for df in queryset:
        if df.url != '':
            df.download()
upload_datasource.short_description = "Upload de geselecteerde gegevensbronnen naar de server"

def update_parameters(modeladmin, request, queryset):
    for df in queryset:
        files = df.sourcefiles.all()
#         n = min(10,files.count())
#         files = files.reverse()[:n] # take last 10 files only
        df.update_parameters(files=files)
update_parameters.short_description = "Update de parameterlijst van de geselecteerde gegevensbronnen"

def replace_parameters(modeladmin, request, queryset):
    for df in queryset:
        count = df.parametercount()
        df.parameter_set.all().delete()
        logger.info('%d parameters deleted for datasource %s' % (count or 0, df))
    update_parameters(modeladmin, request, queryset)
            
replace_parameters.short_description = "Vervang de parameterlijst van de geselecteerde gegevensbronnen"

def update_thumbnails(modeladmin, request, queryset):
    # group queryset by datasource
    group = {}
    for p in queryset:
        if not p.datasource in group:
            group[p.datasource] = []
        group[p.datasource].append(p)
         
    for fil,parms in group.iteritems():
        data = fil.get_data()
        for p in parms:
            p.make_thumbnail(data=data)
            p.save()
    
update_thumbnails.short_description = "Thumbnails vernieuwen van geselecteerde parameters"

def generate_series(modeladmin, request, queryset):
    for p in queryset:
        try:
            series, created = p.series_set.get_or_create(name = p.name, description = p.description, unit = p.unit, user = request.user)
            series.replace()
        except Exception as e:
            logger.error('ERROR creating series %s: %s' % (p.name, e))
generate_series.short_description = 'Standaard tijdreeksen aanmaken voor geselecteerde parameters'

def download_series(modeladmin, request, queryset):
    ds = set([series.datasource() for series in queryset])
    for d in ds:
        d.download()
download_series.short_description = 'Bronbestanden van geselecteerde tijdreeksen downloaden'

#TODO: convert to celery
from django.utils.text import slugify
from django.conf import settings
import os,tempfile
from zipfile import ZipFile
from threading import Thread

from django.core.mail import send_mail
from datetime import datetime, timedelta
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

def email_series_zip(request, queryset, zf):
    if not queryset:
        logger.warning('Not sending emails: empty queryset')
    elif not request.user.email:
        logger.warning('Not sending emails: no email address for user %s' % request.user.username)
    else:
        url = request.build_absolute_uri(settings.EXPORT_URL+os.path.basename(zf.filename))
        logger.debug('Preparing zip file %s' % url)
        for series in queryset:
            filename = slugify(unicode(series)) + '.csv'
            logger.debug('adding %s' % filename)
            print 'adding %s' % filename
            csv = series.to_csv()
            zf.writestr(filename,csv)
        zf.close()
        logger.debug('Done, sending email with link to %s (%s)' % (request.user.username, request.user.email))
        
        message = render_to_string('data/notify_email_nl.html', {'name': request.user.first_name or request.user.username,
                                                                 'domain': request.META.get('HTTP_HOST','acaciadata.com'),
                                                                 'link': url,
                                                                 'expire': (datetime.today() + timedelta(days=4)).date()
                                                                 })
        non_html_message = 'Beste {user},\n\nDe export van de geselecteerde tijdreeksen van {{domain}} is gereed. Je kan het zip bestand met de resultaten downloaden van {url}.\nDe download link verloopt op {{expire}}. Na deze datum wordt het bestand van onze server verwijderd.\n\nMet vriendelijke groet,\nAcacia Water'.format(user=request.user.first_name or request.user.username, url=url,domain = request.META.get('HTTP_HOST','acaciadata.com'),expire= (datetime.today() + timedelta(days=4)).date())
        
        success = send_mail(subject='Tijdreeksen gereed',
    
                   message=non_html_message,
                   from_email = 'srmoquette@gmail.com',
                   recipient_list=[request.user.email],
                   html_message = message
                )
        if success == 0:
            logger.error('Failed to send email')
        else:
            logger.debug('Email sent')

def download_series_zip(modeladmin, request, queryset):
    if not os.path.exists(settings.EXPORT_ROOT):
        os.mkdir(settings.EXPORT_ROOT)
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.zip', dir=settings.EXPORT_ROOT, delete=False)
    zipfile = ZipFile(tmp,'w')
    series = list(queryset)
    t = Thread(target=email_series_zip, args=(request,series,zipfile))
    t.start()
    
download_series_zip.short_description = 'Geselecteerde tijdreeksen converteren naar csv en link naaar zip bestand emailen'
    
def refresh_series(modeladmin, request, queryset):
    for s in Series.objects.get_real_instances(queryset):
        s.update(start=s.tot())
refresh_series.short_description = 'Geselecteerde tijdreeksen actualiseren'

def replace_series(modeladmin, request, queryset):
    for s in Series.objects.get_real_instances(queryset):
        if isinstance(s,ManualSeries): # Skip manual series (all points will be deleted!)
            continue
        s.replace()
replace_series.short_description = 'Geselecteerde tijdreeksen opnieuw aanmaken'

def empty_series(modeladmin, request, queryset):
    for s in Series.objects.get_real_instances(queryset):
        s.datapoints.all().delete()
empty_series.short_description = 'Data van geselecteerde tijdreeksen verwijderen'

def series_thumbnails(modeladmin, request, queryset):
    for s in Series.objects.get_real_instances(queryset):
        s.make_thumbnail()
        s.save()
series_thumbnails.short_description = "Thumbnails van tijdreeksen vernieuwen"

def copy_series(modeladmin, request, queryset):
    for s in queryset:
        name = 'kopie van %s' % (s.name)
        copy = 1 
        while Series.objects.filter(name = name).exists():
            copy += 1
            name = 'kopie %d van %s' % (copy, s.name)
        s.pk = None
        s.name = name
        s.user = request.user
        s.save()
copy_series.short_description = "Geselecteerde tijdreeksen dupliceren"

def update_series_properties(modeladmin, request, queryset):
    for s in queryset:
        s.getproperties().update()
update_series_properties.short_description = "Eigenschappen van geselecteerde tijdreeksen bijwerken"

def set_locatie(modeladmin, request, queryset):
    for m in queryset:
        series = list(m.series_set.all())
        series = series.extend(m.series())
        if series:
            series = set(series)
            for s in series:
                if not s.mlocatie:
                    s.mlocatie = m
                    s.save()
set_locatie.short_description = 'Update meetlocatie eigenschap van gerelateerde tijdreeksen'
        
def copy_charts(modeladmin, request, queryset):
    for c in queryset:
        name = 'kopie van %s' % (c.name)
        copy = 1 
        while Chart.objects.filter(name = name).exists():
            copy += 1
            name = 'kopie %d van %s' % (copy, c.name)
        c.pk = None
        c.name = name
        c.user = request.user
        c.save()
copy_charts.short_description = "Geselecteerde grafieken dupliceren"

def create_grid(modeladmin, request, queryset):
    ''' create grid from selected timeseries '''
    name='Naamloos'
    index=0
    while Grid.objects.filter(name=name).count()>0:
        index += 1
        name = 'Naamloos%d' % index
    grid = Grid.objects.create(name=name,title=name,description=name,user=request.user,percount=0)
    order = 1
    for s in queryset:
        name = s.name
        # use the last  number in the grid name as index: R1VV(13) -> 13
        match = re.findall(r'\d+',name)
        if match:
            order = int(match[-1])
        grid.series.create(series=s, order=order)
        order += 1
create_grid.short_description = "Grid maken met geselecteerde tijdreeksen"

def update_grid(modeladmin, request, queryset):
    ''' update time series for selected grids '''
    group = []
    for g in queryset:
        for cs in g.series.all():
            s = cs.series
            ds = s.datasource
            if ds is not None:
                if not ds in group:
                    ds.download()
                    group.append(ds)
    for g in queryset:
        for cs in g.series.all():
            s = cs.series
            s.update()
            
update_grid.short_description = "Grid bijwerken"

def test_kental(modeladmin, request, queryset):
    for k in queryset:
        print k.get_value()

def update_kental(modeladmin, request, queryset):
    for k in queryset:
        k.update()
                