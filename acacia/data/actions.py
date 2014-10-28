from .shortcuts import meteo2locatie
from .models import Chart, Series
import logging
logger = logging.getLogger(__name__)

def meteo_toevoegen(modeladmin, request, queryset):
    pass
    for loc in queryset:
        meteo2locatie(loc,user=request.user)
meteo_toevoegen.short_description = "Meteostation, neerslagstation en regenradar toevoegen"

def upload_datasource(modeladmin, request, queryset):
    for df in queryset:
        if df.url != '':
            df.download()
upload_datasource.short_description = "Upload de geselecteerde datasources naar de server"

def update_parameters(modeladmin, request, queryset):
    for df in queryset:
        df.update_parameters()
update_parameters.short_description = "Update de parameterlijst van de geselecteerde datasources"

def replace_parameters(modeladmin, request, queryset):
    for df in queryset:
        count = df.parametercount()
        df.parameter_set.all().delete()
        logger.info('%d parameters deleted for datasource %s' % (count or 0, df))
        df.update_parameters()    
replace_parameters.short_description = "Vervang de parameterlijst van de geselecteerde datasources"

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
            series = p.series_set.get_or_create(name = p.name, description = p.description, unit = p.unit, user = request.user)
            series.replace()
        except Exception as e:
            logger.error('ERROR creating series %s: %s' % (p.name, e))
generate_series.short_description = 'Standaard tijdreeksen aanmaken voor geselecteerde parameters'

def download_series(modeladmin, request, queryset):
    ds = set([series.datasource() for series in queryset])
    for d in ds:
        d.download()
download_series.short_description = 'Bronbestanden van geselecteerde tijdreeksen downloaden'
    
def refresh_series(modeladmin, request, queryset):
    #download_series(modeladmin, request, queryset)
    for s in queryset:
        s.update()
refresh_series.short_description = 'Geselecteerde tijdreeksen actualiseren'

def replace_series(modeladmin, request, queryset):
    #download_series(modeladmin, request, queryset)
    for s in queryset:
        s.replace()
replace_series.short_description = 'Geselecteerde tijdreeksen opnieuw aanmaken'

def empty_series(modeladmin, request, queryset):
    for s in queryset:
        s.datapoints.all().delete()
empty_series.short_description = 'Data van geselecteerde tijdreeksen verwijderen'

def series_thumbnails(modeladmin, request, queryset):
    for s in queryset:
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
