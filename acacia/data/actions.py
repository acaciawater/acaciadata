from .shortcuts import meteo2locatie
from .models import Chart, Series, Grid, ManualSeries

import logging, re
from django.contrib.gis.geos.point import Point
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.db import transaction

logger = logging.getLogger(__name__)

def sourcefile_dimensions(modeladmin, request, queryset):
    '''sourcefile doorlezen en eigenschappen updaten (start, stop, rows etc)'''
    for sf in queryset:
        #sf.get_dimensions()
        sf.save() # pre-save signal calls get_dimensions
sourcefile_dimensions.short_description=_('Read selected sourcefiles and update properties')

def datasource_dimensions(modeladmin, request, queryset):
    '''alle sourcefiles doorlezen en eigenschappen updaten (start, stop, rows etc)'''
    for ds in queryset:
        sourcefile_dimensions(modeladmin, request, ds.sourcefiles.all())
datasource_dimensions.short_description=_('Read sourcefiles of selected datasources and update properties')

def meetlocatie_aanmaken(modeladmin, request, queryset):
    '''standaard meetlocatie aanmaken op zelfde locatie als projectlocatie '''
    for p in queryset:
        p.meetlocatie_set.create(name=p.name,location=p.location, description=p.description)
meetlocatie_aanmaken.short_description = _('Create measuring point at selected locations')
        
def meteo_toevoegen(modeladmin, request, queryset):
    for loc in queryset:
        meteo2locatie(loc,user=request.user)
meteo_toevoegen.short_description = _('Create weather stations')

def upload_datasource(modeladmin, request, queryset):
    for df in queryset:
        df.download()
upload_datasource.short_description = _('Upload selected datasources to the server')

def update_parameters(modeladmin, request, queryset):
    for df in queryset:
        files = df.sourcefiles.all()
#         n = min(10,files.count())
#         files = files.reverse()[:n] # take last 10 files only
        df.update_parameters(files=files)
update_parameters.short_description = _('Update parameter list for selected datasources')

def replace_parameters(modeladmin, request, queryset):
    for df in queryset:
        count = df.parametercount()
        df.parameter_set.all().delete()
        logger.info(_('%(count)d parameters deleted for datasource %(datasource)s') % {'count':count or 0, 'datasource':df})
    update_parameters(modeladmin, request, queryset)
            
replace_parameters.short_description = _("Replace parameter list of selected datasoures")

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
    
update_thumbnails.short_description = _("Replace thumbnails of selected parameters")

def generate_series(modeladmin, request, queryset):
    nok = 0
    nbad = 0
    for p in queryset:
        try:
            data = p.get_data()
            ds = p.datasource
            
            # get list of all locations
            locs = set(ds.locations.all())

            locs.add(ds.meetlocatie)
            
            # create series for all locations
            for loc in locs:
                if loc in data:
                    df = data[loc]
                elif loc.name in data:
                    df = data[loc.name]
                else:
                    continue
                logger.debug(_('Creating series {} for location {}').format(p.name, loc.name))
                series, created = p.series_set.get_or_create(mlocatie = loc, name = p.name, 
                                                         defaults= {'description': p.description, 'unit': p.unit, 'user': request.user})
                try:
                    series.replace(df)
                    nok += 1
                except Exception as e:
                    logger.error(_('ERROR creating series %(series)s for location %(loc)s: %(ex)s') % {'series':p.name, 'loc':loc.name, 'ex':e})
        except Exception as e:
            nbad += 1
            logger.error(_('ERROR creating series %(name)s: %(ex)s') % {'name':p.name, 'ex':e})
    if nok:
        messages.success(request, _('{} series successfully created.').format(nok))
    if nbad:
        messages.error(request, _('{} series were not created.').format(nbad))
        
generate_series.short_description = _('Create timeseries for selected parameters')

def generate_datasource_series(modeladmin, request, queryset):
    for ds in queryset:
        ds.update_parameters()
        data = ds.get_data()
        locs = set(ds.locations.all())
        locs.add(ds.meetlocatie)
        
        for p in ds.parameter_set.all():
            try:
                # create series for all locations
                for loc in locs:
                    if loc in data:
                        df = data[loc]
                    elif loc.name in data:
                        df = data[loc.name]
                    else:
                        continue
                    logger.debug(_('Creating series {} for location {}').format(p.name, loc.name))
                    series, created = p.series_set.get_or_create(mlocatie = loc, name = p.name, 
                                                             defaults= {'description': p.description, 'unit': p.unit, 'user': request.user})
                    try:
                        series.replace(df)
                    except Exception as e:
                        logger.error(_('ERROR creating series %(name)s for location %(loc)s: %(ex)s') % {'name':p.name, 'loc':loc.name, 'ex':e})
            except Exception as e:
                logger.error(_('ERROR creating series %(name)s: %(ex)s') % {'name':p.name, 'ex':e})

generate_datasource_series.short_description = _('Create timeseries for all parameters in selected datasources')

def update_datasource_series(modeladmin, request, queryset):
    for ds in queryset:
        series = ds.getseries()
        tots = [s.tot() for s in series if s.aantal()]
        oldest = min(tots) if tots else None
        data = ds.get_data(start=oldest)
        for s in ds.getseries():
            s.update(data=data)
update_datasource_series.short_description = _('Update timeseries of selected datasources')
        
def download_series(modeladmin, request, queryset):
    ds = set([series.datasource() for series in queryset])
    for d in ds:
        d.download()
download_series.short_description = _('Download source files of selected timeseries')

def filter_series(modeladmin, request, queryset):
    for s in queryset:
        if s.has_filters():
            data = s.to_pandas()
            filtered_data = s.do_filter(data)
            s.replace_data(filtered_data)
filter_series.short_description = _('Apply filtering on selected timeseries')

from django.utils.text import slugify
from django.conf import settings
import os,tempfile
from zipfile import ZipFile
from threading import Thread

from datetime import datetime, timedelta
from django.template.loader import render_to_string

def store_csv(queryset, zf, **kwargs):
    for series in queryset:
        ml = series.meetlocatie()
        if ml:
            src = slugify('{}-{}'.format(ml.name, series.name))
        else:
            ds = series.datasource()
            if ds:
                src = slugify('{}-{}'.format(ds.name, series.name))
            else:
                src = slugify(unicode(series))
        filename = src + '.csv'
        logger.debug(_('adding %s') % filename)
        csv = series.to_csv(**kwargs)
        zf.writestr(filename,csv)

def email_series_zip(request, queryset, zf, store=store_csv):
    if not queryset:
        logger.warning(_('Not sending emails: empty queryset'))
    elif not request.user.email:
        logger.error(_('Not sending emails: no email address for user %s') % request.user.username)
    else:
        url = request.build_absolute_uri(settings.EXPORT_URL+os.path.basename(zf.filename))
        logger.debug(_('Preparing zip file %s') % url)
        datatype = request.GET.get('type','valid')
        store(queryset, zf, type=datatype)
        zf.close()
        name = request.user.get_full_name() or request.user.username
        logger.debug(_('Done, sending email with link to %(name)s (%(email)s)') % {'name':name, 'email':request.user.email})
        
        name=request.user.first_name or request.user.username
        domain = request.META.get('HTTP_HOST','acaciadata.com')
        expire=(datetime.today() + timedelta(days=4)).date()
        html_message = render_to_string('data/notify_email_nl.html', {'name': name,'domain': domain,'link': url,'expire': expire})
        message = render_to_string('data/notify_email_nl.txt', {'name': name,'domain': domain,'link': url,'expire': expire})
        success = request.user.email_user(subject=_('Timeseries ready'), message=message, html_message = html_message)
        if success == 0:
            logger.error(_('Failed to send email'))
        else:
            logger.debug(_('Email sent'))

def download_series_zip(modeladmin, request, queryset, store=store_csv):
    if not os.path.exists(settings.EXPORT_ROOT):
        os.mkdir(settings.EXPORT_ROOT)
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.zip', dir=settings.EXPORT_ROOT, delete=False)
    zipfile = ZipFile(tmp,'w')
    series = list(queryset)
    t = Thread(target=email_series_zip, args=(request,series,zipfile,store))
    t.start()
download_series_zip.short_description = _('Convert selected timeseries to csv format and email link to zip file')
    
import StringIO
from django.http import HttpResponse

def download_series_csv(modeladmin, request, queryset):
    io = StringIO.StringIO()
    zf = ZipFile(io,'w')
    series_type = request.GET.get('type','valid')
    for series in queryset:
        filename = slugify(series.name) + '.csv'
        csv = series.to_csv(type=series_type)
        zf.writestr(filename,csv)
    zf.close()
    resp = HttpResponse(io.getvalue(), content_type = "application/x-zip-compressed")
    resp['Content-Disposition'] = 'attachment; filename=series.zip'
    return resp
download_series_csv.short_description = _('Download selected timeseries as zip file')
    
def refresh_series(modeladmin, request, queryset):
    for s in Series.objects.get_real_instances(queryset):
        s.update(start=s.tot())
refresh_series.short_description = _('Update selected timeseries')

def replace_series(modeladmin, request, queryset):
    for s in Series.objects.get_real_instances(queryset):
        if isinstance(s,ManualSeries): # Skip manual series (all points will be deleted!)
            continue
        s.replace()
replace_series.short_description = _('Recreate selected timeseries')

def empty_series(modeladmin, request, queryset):
    for s in Series.objects.get_real_instances(queryset):
        s.datapoints.all().delete()
empty_series.short_description = _('Delete datapoints from selected timeseries')

def series_thumbnails(modeladmin, request, queryset):
    for s in Series.objects.get_real_instances(queryset):
        s.make_thumbnail()
        s.save()
series_thumbnails.short_description = _("Refresh thumbnails")

def copy_series(modeladmin, request, queryset):
    for s in queryset:
        name = _('copy of %s') % (s.name)
        copy = 1 
        while Series.objects.filter(name = name).exists():
            copy += 1
            name = _('copy %(count)d of %(name)s') % {'count':copy, 'name':s.name}
        s.pk = None
        s.name = name
        s.user = request.user
        s.save()
copy_series.short_description = _("Copy selected timeseries")

def update_series_properties(modeladmin, request, queryset):
    for s in queryset:
        s.getproperties().update()
update_series_properties.short_description = _("Update properties of selected timeseries")

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
set_locatie.short_description = _('Set location of selected timeseries')
        
def copy_charts(modeladmin, request, queryset):
    for c in queryset:
        name = _('copy of %s') % (c.name)
        copy = 1 
        while Chart.objects.filter(name = name).exists():
            copy += 1
            name = _('copy %(count)d of %(name)s') % {'count':copy, 'name':c.name}
        c.pk = None
        c.name = name
        c.user = request.user
        c.save()
copy_charts.short_description = _("Copy selected charts")

def create_grid(modeladmin, request, queryset):
    ''' create grid from selected timeseries '''
    name=_('Untitled')
    index=0
    while Grid.objects.filter(name=name).count()>0:
        index += 1
        name = _('Untitled%d') % index
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
create_grid.short_description = _("Created grid from selected timeseries")

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
update_grid.short_description = _("Update grid")


def test_kental(modeladmin, request, queryset):
    for k in queryset:
        print k.get_value()

def update_kental(modeladmin, request, queryset):
    for k in queryset:
        k.update()

def generate_locations(modeladmin, request, queryset):
    from acacia.data.util import toRD
    '''generates meetlocaties from a datasource'''
    ncreated = 0
    for ds in queryset:
        projectlocatie = ds.projectlocatie()
        locs = ds.get_locations()
        for key,values in locs.iteritems():
            desc = values.get('description',None)
            loc = Point(values['coords'],srid=values['srid'])
            loc = toRD(loc)
            try:
                mloc, created = projectlocatie.meetlocatie_set.get_or_create(name=key,defaults={'description': desc,'location':loc})
                if created:
                    logger.debug(_('Created measuring point {}').format(unicode(mloc)))
                    ncreated += 1
                    try:
                        ds.locations.add(mloc)
                    except Exception as e:
                        logger.error(_('Cannot add secondary measuring point {loc} to datasource {ds}: {ex}').format(loc=mloc, ds=ds, ex=e))
            except Exception as e:
                logger.exception(_('Cannot create measuring point {}').format(key))
    logger.info(_('{} new locations created').format(ncreated))
generate_locations.short_description = _('Create measuring points for selected datasources')
