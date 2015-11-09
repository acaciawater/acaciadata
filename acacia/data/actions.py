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
upload_datasource.short_description = "Upload de geselecteerde datasources naar de server"

def update_parameters(modeladmin, request, queryset):
    for df in queryset:
        files = df.sourcefiles.all()
#         n = min(10,files.count())
#         files = files.reverse()[:n] # take last 10 files only
        df.update_parameters(files=files)
update_parameters.short_description = "Update de parameterlijst van de geselecteerde datasources"

def replace_parameters(modeladmin, request, queryset):
    for df in queryset:
        count = df.parametercount()
        df.parameter_set.all().delete()
        logger.info('%d parameters deleted for datasource %s' % (count or 0, df))
    update_parameters(modeladmin, request, queryset)
            
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
