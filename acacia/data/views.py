# -*- coding: utf-8 -*-
import simplejson as json
import re,logging
from django.views.generic.list import ListView
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from .models import Project, ProjectLocatie, MeetLocatie, Datasource, Series, Chart, Grid, Dashboard, TabGroup, KeyFigure, Formula
from .util import datasource_as_zip, datasource_as_csv, meetlocatie_as_zip, series_as_csv, chart_as_csv
from .actions import download_series_zip
from django.views.decorators.gzip import gzip_page
from django.conf import settings
from django.contrib.auth.decorators import login_required
from dateutil.parser import parse
from acacia.data.models import aware
import pandas as pd
from acacia.data.util import resample_rule, to_millis
from django.utils.translation import ugettext as _

logger = logging.getLogger(__name__)

def DatasourceAsZip(request,pk):
    ''' Alle bestanden in datasource downloaden als zip file '''
    ds = get_object_or_404(Datasource,pk=pk)
    return datasource_as_zip(ds)

def DatasourceAsCsv(request,pk):
    ''' Datasource downloaden als csv file met een parameter in elke kolom '''
    ds = get_object_or_404(Datasource,pk=pk)
    return datasource_as_csv(ds)

def MeetlocatieAsZip(request,pk):
    loc = get_object_or_404(MeetLocatie,pk=pk)
    return meetlocatie_as_zip(loc)

def SeriesAsCsv(request,pk):
    s = get_object_or_404(Series,pk=pk)
    return series_as_csv(s)

@login_required
def DownloadSeriesAsZip(request,source,series):
    ''' Tijdreeksen downloaden als zip file '''
    download_series_zip(None, request, series) # reuse method from admin.actions. Runs in separate thread
    return redirect(request.META.get('HTTP_REFERER','/'))

def EmailProject(request, pk):
    p = get_object_or_404(Project,pk=pk)
    return DownloadSeriesAsZip(request, unicode(p), p.series())

def EmailProjectLocatie(request, pk):
    loc = get_object_or_404(ProjectLocatie,pk=pk)
    return DownloadSeriesAsZip(request, unicode(loc), loc.series())

def EmailMeetLocatie(request,pk):
    loc = get_object_or_404(MeetLocatie,pk=pk)
    return DownloadSeriesAsZip(request, unicode(loc), loc.series())

def EmailDatasource(request, pk):
    ds = get_object_or_404(Datasource,pk=pk)
    return DownloadSeriesAsZip(request, unicode(ds), ds.getseries())

@gzip_page
def SeriesToJson(request, pk):
    s = get_object_or_404(Series,pk=pk)
    pts = s.to_array()        
    # convert datetime to javascript datetime using unix timetamp conversion
    j = json.dumps(list(pts), ignore_nan = True, default=to_millis)
    return HttpResponse(j, content_type='application/json')

def SeriesToDict(request, pk):
    s = get_object_or_404(Series,pk=pk)
    points = [{'date':p.date.date(),'time': p.date.time(), 'value':p.value} for p in s.to_array()]
    j = json.dumps(points, ignore_nan = True, default=lambda x: str(x))
    return HttpResponse(j, content_type='application/json')

@gzip_page
def ChartToJson(request, pk):
    c = get_object_or_404(Chart,pk=pk)
    start = request.GET.get('start', c.auto_start())
    stop = request.GET.get('stop', c.stop)
    maxpts = int(request.GET.get('max',0))
    data = {}
    for cs in c.series.all():
        
        def getseriesdata(s):
            pts = list(s.to_array(start=start,stop=stop))
            num = len(pts)
            
            #resample test
            if num>0 and cs.type == 'line':
                x,y = zip(*pts)
                f = pd.Series(data=y,index=x).resample(rule='H').mean()
                f[pd.isnull(f)]=''
                pts = zip(f.index,f.values)

            if maxpts>0:
                if num > maxpts:
                    # thin series
                    date_range = pts[-1][0] - pts[0][0]
                    delta = date_range / maxpts
                    rule = resample_rule(delta)
                    x,y = zip(*pts)
                    resampled = pd.Series(data=y,index=x).resample(rule)
                    pts = zip(resampled.index,resampled.values)
            return pts

        pts = getseriesdata(cs.series)
        if cs.type == 'area' and cs.series2:
            try:
                pts2 = getseriesdata(cs.series2)
                pts = [[p1[0],p1[1],p2[1]] for p1,p2 in zip(pts,pts2)]
            except:
                logger.exception(_('Cannot align series {a} and {b} for area fill in chart {c}').format(a=str(cs.series), b=str(cs.series2), c=str(c)))
                # series need to be aligned
                pass
        data['series_%d' % cs.series.id] = pts
        
    return HttpResponse(json.dumps(data, default=to_millis), content_type='application/json')

@gzip_page
def GridToJson(request, pk):
    g = get_object_or_404(Grid,pk=pk)
    start = g.auto_start()
    rowdata = []
    y = g.ymin
    for cs in g.series.all():
        s = cs.series
        if g.stop is None:
            row = [[p.date,y,p.value*g.scale] for p in s.datapoints.filter(date__gt=start).order_by('date')]
        else:
            row = [[p.date,y,p.value*g.scale] for p in s.datapoints.filter(date__gt=start, date__lt=g.stop).order_by('date')]
        y += g.rowheight
        rowdata.extend(row)
    data = {'grid': rowdata, 'min': min(rowdata), 'max': max(rowdata) }
    return HttpResponse(json.dumps(data,default=to_millis), content_type='application/json')
    
def get_key(request, pk):
    key = get_object_or_404(KeyFigure, pk)
    result = {'name': key.name, 'id': key.pk, 'value': key.get_value()}
    return HttpResponse(json.dumps(result), content_type='application/json')

def get_keys(request):
    result = {}
    for key in KeyFigure.objects.all():
        result[key.name] = {'id': key.pk, 'value': key.get_value()}
    return HttpResponse(json.dumps(result), content_type='application/json')

def ChartAsCsv(request,pk):
    c = get_object_or_404(Chart,pk=pk)
    return chart_as_csv(c)

# def tojs(d):
#     return 'Date.UTC(%d,%d,%d,%d,%d,%d)' % (d.year, d.month-1, d.day, d.hour, d.minute, d.second)
# 
# def date_handler(obj):
#     return tojs(obj) if isinstance(obj, (datetime.date, datetime.datetime,)) else obj

from .tasks import update_meetlocatie, update_datasource

def UpdateMeetlocatie(request,pk):
    update_meetlocatie(pk)
    return redirect(request.GET['next'])

def UpdateDatasource(request,pk):
    nxt = request.GET['next']
    update_datasource(pk)
    return redirect(nxt)

class DatasourceDetailView(DetailView):
    model = Datasource

class ProjectView(DetailView):
    model = Project       
    
class ProjectListView(ListView):
    model = Project

class ProjectDetailView(DetailView):
    model = Project

    def get_context_data(self, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(**kwargs)
        project = self.get_object()
        content = []
        for loc in project.projectlocatie_set.all():
            pos = loc.latlon()
            content.append({
                            'id': loc.id,
                            'name': loc.name,
                            'lat': pos.y,
                            'lon': pos.x,
                            'info': render_to_string('data/projectlocatie_info.html', {'object': loc})
                            })
        context['content'] = json.dumps(content)
        context['maptype'] = 'TERRAIN'
        context['apikey'] = settings.GOOGLE_MAPS_API_KEY
        return context

class ProjectLocatieDetailView(DetailView):
    model = ProjectLocatie
    
    def get_context_data(self, **kwargs):
        context = super(ProjectLocatieDetailView, self).get_context_data(**kwargs)
        content = render_to_string('data/projectlocatie_info.html', {'object': self.get_object()})
        context['content'] = json.dumps(content)
        context['maptype'] = 'SATELLITE'
        context['zoom'] = 14
        context['apikey'] = settings.GOOGLE_MAPS_API_KEY
        return context

class MeetLocatieDetailView(DetailView):
    model = MeetLocatie
    
    def get_context_data(self, **kwargs):
        context = super(MeetLocatieDetailView, self).get_context_data(**kwargs)
        content = render_to_string('data/meetlocatie_info.html', {'object': self.get_object()})
        context['content'] = json.dumps(content)
        context['maptype'] = 'SATELLITE'
        context['zoom'] = 16
        context['apikey'] = settings.GOOGLE_MAPS_API_KEY
        return context
        
class SeriesView(DetailView):
    model = Series

    def get_context_data(self, **kwargs):
        context = super(SeriesView, self).get_context_data(**kwargs)
        ser = self.get_object()
        unit = ser.unit
        options = {
#             'rangeSelector': { 'enabled': True,
#                               'inputEnabled': True,
#                               },
#             'loading': {'style': {'backgroundColor': 'white', 'fontFamily': 'Arial', 'fontSize': 'small'},
#                         'labelStyle': {'fontWeight': 'normal'},
#                         'hideDuration': 0,
#                         },
            'chart': {'type': ser.type, 
                      'animation': False, 
                      'zoomType': 'x',
                      'events': {'load': None},
                      },
            'title': {'text': ser.name},
            'xAxis': {'type': 'datetime'},
            'yAxis': [],
            'tooltip': {'valueSuffix': ' '+(unit or ''),
                        'valueDecimals': 2
                       }, 
            'legend': {'enabled': False},
            'plotOptions': {'line': {'marker': {'enabled': False}}},            
            'credits': {'enabled': True, 
                        'text': 'acaciawater.com', 
                        'href': 'http://www.acaciawater.com',
                       }
            }
           
        allseries = []
        title = ser.name if (unit is None or len(unit)==0) else unit
        options['yAxis'].append({
                                 'title': {'text': title},
                                 })
        pts = [] #[[p.date,p.value] for p in ser.datapoints.all().order_by('date')]
        sop = {'name': ser.name,
               'type': ser.type,
               'data': pts,
               'turboThreshold': 0}
        if ser.type == 'scatter':
            sop['tooltip'] = {'headerFormat': '<small>{point.key}</small><br/><table>',
                              'pointFormat': '<tr><td style="color:{series.color}">{series.name}</td>\
                                <td style = "text-align: right">: <b>{point.y}</b></td></tr>'}
        allseries.append(sop)
        options['series'] = allseries
        context['options'] = json.dumps(options,default=to_millis)
        context['theme'] = ' None' #ser.theme()
        return context

def parserep(r):
    from dateutil.relativedelta import relativedelta
    pattern = r'(?P<rep>\d*)(?P<how>[hdwmy])'
    match = re.match(pattern, r,re.IGNORECASE)
    if match:
        rep = match.group('rep') or 1
        how = match.group('how')
        if how == 'h':
            delta = relativedelta(hours=int(rep))
        elif how == 'd':
            delta = relativedelta(days=int(rep))
        elif how == 'w':
            delta = relativedelta(weeks=int(rep))
        elif how == 'm':
            delta = relativedelta(months=int(rep))
        elif how == 'y':
            delta = relativedelta(years=int(rep))
        return delta
    return None

class ChartBaseView(TemplateView):
    template_name = 'data/plain_chart.html'

    def get_json(self, chart):
        options = {
            'chart': {'animation': False, 
                      'zoomType': 'x',
                      'events': {'load': None},
                      },
            'title': {'text': chart.title},
            'xAxis': {'type': 'datetime','plotBands': []},
            'yAxis': [],
            'tooltip': {'valueDecimals': 2,
                        'shared': True,
                       }, 
            'legend': {'enabled': chart.series.count() > 1},
            'plotOptions': {'line': {'marker': {'enabled': False}}, 'series': {'connectNulls': True},
                              'column': {'allowpointSelect': True, 'pointPadding': 0.01, 'groupPadding': 0.01}},
            'credits': {'enabled': True, 
                        'text': 'acaciawater.com', 
                        'href': 'http://www.acaciawater.com',
                       },
            'exporting' :{
                    'sourceWidth': 1080,
                    'sourceHeight': 600,
#                     'scale': 2,
#                     'chartOptions' :{
#                         'title': {'style': {'fontSize': 0 }},                 # 0 gemaakt omdat titel niet wordt overgenomen
#                         'xAxis': {'labels': {'style': {'fontSize': 15 }}},
#                         'yAxis': {'labels': {'style': {'fontSize': 15 }}},
#                         'legend': {'itemStyle': {'fontSize': 15 },'padding': 1,},           
#                         'credits': {'enabled': False}
#                    },
                }
            }
        if chart.start:
            options['xAxis']['min'] = chart.start
        if chart.stop:
            options['xAxis']['max'] = chart.stop
        allseries = []

        tmin = chart.start
        tmax = chart.stop
        ymin = None
        ymax = None 
        
        num_series = chart.series.count()

        for _,s in enumerate(chart.series.all()):
            ser = s.series
            if tmin:
                tmin = min(tmin,s.t0 or ser.van() or chart.start or tmin)
            else:
                tmin = s.t0 or ser.van() or chart.start
            if tmax:
                tmax = max(tmax,s.t1 or ser.tot() or chart.stop or tmax)
            else:
                tmax = s.t1 or ser.tot() or chart.stop
            if ymin:
                ymin = min(ymin,s.y0 or ser.minimum())
            else:
                ymin = s.y0 or ser.minimum()
            if ymax:
                ymax = max(ymax,s.y1 or ser.maximum())
            else:
                ymax = s.y1 or ser.maximum()
            
            try:
                deltat = (ser.tot()-ser.van()).total_seconds() / ser.aantal() * 1000
            except:
                deltat = 24 * 3600000 # 1 day                
            options['yAxis'].append({
                                     'title': {'text': s.label},
                                     'opposite': 0 if s.axislr == 'l' else 1,
                                     'min': s.y0,
                                     'max': s.y1
                                     })
            pts = []
            name = s.name
            if name is None or name == '':
                name = ser.name
                
            if not ser.validated:
                # append asterisk to name when series has not been validated
                if isinstance(ser,Formula):
                    for dep in ser.get_dependencies():
                        if not dep.validated:
                            name += '*'
                            break
                else:
                    name += '*'
                 
            sop = {'name': name,
                   'id': 'series_%d' % ser.id,
                   'type': s.type,
                   'yAxis': s.axis-1,
                   'data': pts}
            if not s.color is None and len(s.color)>0:
                sop['color'] = s.color
            if s.type == 'scatter':
                sop['tooltip'] = {'valueSuffix': ' '+ser.unit,
                                  'headerFormat': '<small>{point.key}</small><br/><table>',
                                  'pointFormat': '<tr><td style="color:{series.color}">{series.name}</td>\
                                    <td style = "text-align: right">: <b>{point.y}</b></td></tr>'}
            
            else:
                sop['tooltip'] = {'valueSuffix': ' ' + ser.unit}                           
            if s.type == 'column':
                if s.stack is not None:
                    sop['stacking'] = s.stack
                if num_series > 1:
                    sop['pointRange'] = deltat
            if s.type == 'area' and s.series2:
                sop['type'] = 'arearange'
                sop['fillOpacity'] = 0.3
            allseries.append(sop)
        options['series'] = allseries
        
        for band in chart.plotband_set.all():
            if band.orientation == 'h':
                ax = options['yAxis'][band.axis-1]
                lo = float(band.low)
                hi = float(band.high)
                every = max(1,float(band.repetition))
                b = []
                for i in range(20):
                    if lo < ymax:
                        b.append(
                            {'color': band.style.fillcolor, 
                             'borderWidth': band.style.borderwidth, 
                             'borderColor': band.style.bordercolor, 
                             'from': lo, 
                             'to': hi, 
                             'label': {'text':band.label},
                             'zIndex': band.style.zIndex
                             })
                        lo += every
                        hi += every
            else:
                ax = options['xAxis']
                lo = parse(band.low)
                hi = parse(band.high)
                
                delta = parserep(band.repetition)
                
                b = []
                for i in range(20):
                    if aware(lo) < aware(tmax):
                        b.append({'color': band.style.fillcolor, 'borderWidth': band.style.borderwidth, 'borderColor': band.style.bordercolor, 'from': lo, 'to': hi, 'label': {'text':band.label}})
                        if delta:
                            lo += delta
                            hi += delta
                
            if not 'plotBands' in ax:
                ax['plotBands'] = []
            ax['plotBands'].extend(b) 
        
        for line in chart.plotline_set.all():
            if line.orientation == 'h':
                ax = options['yAxis'][line.axis-1]
            else:
                ax = options['xAxis']
            line_options = {
                'color': line.style.color,
                'dashStyle': line.style.dashstyle,
                'label': {'text': line.label},
                'value': line.value,
                'width': line.style.width,
                'zIndex': line.style.zIndex
                }
            if not 'plotLines' in ax:
                ax['plotLines'] = []
            ax['plotLines'].append(line_options) 

        return json.dumps(options,default=to_millis)
    
    def get_context_data(self, **kwargs):
        context = super(ChartBaseView, self).get_context_data(**kwargs)
        pk = context.get('pk',1)
        chart = Chart.objects.get(pk=pk)                

        jop = self.get_json(chart)
        context['options'] = jop
        context['chart'] = chart
        context['theme'] = chart.get_theme()
        return context
        
class ChartView(ChartBaseView):
    template_name = 'data/chart_detail.html'
    
class DashView(TemplateView):
    template_name = 'data/dash.html'
     
    def get_context_data(self, **kwargs):
        context = super(DashView,self).get_context_data(**kwargs)
        pk = context.get('pk', None)
        dash = get_object_or_404(Dashboard, pk=pk)
        context['dashboard'] = dash
        return context
    
class TabGroupView(TemplateView):
    template_name = 'data/tabgroup.html'
    
    def get_context_data(self, **kwargs):
        context = super(TabGroupView,self).get_context_data(**kwargs)
        pk = context.get('pk')
        page = int(self.request.GET.get('page', 1))
        group = get_object_or_404(TabGroup, pk=pk)
        dashboards =[p.dashboard for p in group.tabpage_set.order_by('order')]
        context['group'] = group
        page = min(page, len(dashboards))
        if page > 0:
            context['page'] = int(page)
            context['dashboard'] = dashboards[page-1]
        return context    

class DashGroupView(TemplateView):
    template_name = 'data/dashgroup.html'
    
    def get_context_data(self, **kwargs):
        context = super(DashGroupView,self).get_context_data(**kwargs)
        name = context.get('name')
        page = int(self.request.GET.get('page', 1))
        group = get_object_or_404(TabGroup, name__iexact=name)
        dashboards =[p.dashboard for p in group.tabpage_set.order_by('order')]
        context['group'] = group
        page = min(page, len(dashboards))
        if page > 0:
            pages = list(group.pages())
            context['title'] = _('Dashboard %(name)s - %(page)s') % {'name':group.name, 'page': pages[page-1].name}
            context['page'] = int(page)
            context['dashboard'] = dashboards[page-1]
        return context    

class GridBaseView(TemplateView):
    template_name = 'data/plain_map.html'

    def get_json(self, grid):
        x1,y1,z1,x2,y2,z2 = grid.get_extent()
        options = {
            'chart': {
                'type': 'heatmap',
                'zoomType': 'x',
                'events': {'load': None},
            },
            'title': {
                'text': grid.title,
            },
            'subtitle': {
                'text': grid.description,
            },
            'xAxis': {
                'type': 'datetime',
                'min': x1,
                'max': x2 
            },
            'yAxis': {
                'title': {
                    'text': None
                },
                'min': y1,
                'max': y2,
                'startOnTick': False,
                'endOnTick': False,
                'reversed': True
            },
    
            'colorAxis': {
                'stops': [
                    [0, '#3060cf'],
                    [0.5, '#fffbbc'],
                    [0.9, '#c4463a'],
                    [1, '#c4463a']
                ],
                'min': z1,
                'max': z2,
                'startOnTick': False,
                'endOnTick': False,
            },
    
            'legend': {
                        'align': 'right',
                        'layout': 'vertical',
                        'margin': 0,
                        'verticalAlign': 'bottom',
                        'y': -8,
                        'symbolHeight': 600
            },
            
            'series': [{
                'id': 'grid',
                'data' : [], # load using ajax
                'borderWidth': 0,
                'nullColor': '#EFEFEF',
                'colsize': grid.colwidth * 36e5, # hours to milliseconds.
                'rowsize': grid.rowheight,
                'tooltip': {
                    'useHTML': True,
                    'headerFormat': '',
                    'pointFormat': '{point.x: %e %B %Y %H:%M:%S}<br/>'+_('Diepte')+': {point.y}m<br/>' + grid.entity + ': <b>{point.value} '+grid.unit+'</b>',
                    'footerFormat': '',
                    'valueDecimals': 2
                },
            }]
        }

        return json.dumps(options,default=to_millis)
    
    def get_context_data(self, **kwargs):
        context = super(GridBaseView, self).get_context_data(**kwargs)
        pk = context.get('pk',0)
        try:
            grid = Grid.objects.get(pk=pk)
        except:
            grid=None
        jop = self.get_json(grid)
        context['options'] = jop
        context['grid'] = grid
        context['map'] = True
        return context
    
class GridView(GridBaseView):
    template_name = 'data/map.html'

