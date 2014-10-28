from django.views.generic.list import ListView
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from .models import Project, ProjectLocatie, MeetLocatie, Datasource, Series, Chart, Dashboard, TabGroup
from .util import datasource_as_zip, datasource_as_csv, meetlocatie_as_zip, series_as_csv, chart_as_csv
import json
import datetime,time
import re
import logging

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

def SeriesToJson(request, pk):
    s = get_object_or_404(Series,pk=pk)
    points = [[p.date,p.value] for p in s.datapoints.order_by('date')]
    # convert datetime to javascript datetime using unix timetamp conversion
    j = json.dumps(points, default=lambda x: time.mktime(x.timetuple())*1000.0)
    return HttpResponse(j, content_type='application/json')

def ChartToJson(request, pk):
    c = get_object_or_404(Chart,pk=pk)
    data = {}
    for cs in c.series.all():
        s = cs.series
        data['series_%d' % s.id] = [[p.date,p.value] for p in s.datapoints.order_by('date')]
    return HttpResponse(json.dumps(data, default=lambda x: time.mktime(x.timetuple())*1000.0), content_type='application/json')
    
def ChartAsCsv(request,pk):
    c = get_object_or_404(Chart,pk=pk)
    return chart_as_csv(c)

def tojs(d):
    return 'Date.UTC(%d,%d,%d,%d,%d,%d)' % (d.year, d.month-1, d.day, d.hour, d.minute, d.second)

def date_handler(obj):
    return tojs(obj) if isinstance(obj, datetime.date) or isinstance(obj, datetime.datetime) else obj

from .tasks import update_meetlocatie, update_datasource

def UpdateMeetlocatie(request,pk):
    update_meetlocatie(pk)
    referer = request.META.get('HTTP_REFERER',None)
    return redirect(referer)

def UpdateDatasource(request,pk):
    update_datasource(pk)
    referer = request.META.get('HTTP_REFERER',None)
    return redirect(referer)

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
                            'name': loc.name,
                            'lat': pos.y,
                            'lon': pos.x,
                            'info': render_to_string('data/projectlocatie_info.html', {'object': loc})
                            })
        context['content'] = json.dumps(content)
        context['maptype'] = 'TERRAIN'
        return context

class ProjectLocatieDetailView(DetailView):
    model = ProjectLocatie
    
    def get_context_data(self, **kwargs):
        context = super(ProjectLocatieDetailView, self).get_context_data(**kwargs)
        content = render_to_string('data/projectlocatie_info.html', {'object': self.get_object()})
        context['content'] = json.dumps(content)
        context['maptype'] = 'SATELLITE'
        context['zoom'] = 14
        return context

class MeetLocatieDetailView(DetailView):
    model = MeetLocatie
    
    def get_context_data(self, **kwargs):
        context = super(MeetLocatieDetailView, self).get_context_data(**kwargs)
        content = render_to_string('data/meetlocatie_info.html', {'object': self.get_object()})
        context['content'] = json.dumps(content)
        context['maptype'] = 'SATELLITE'
        context['zoom'] = 16
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
            'tooltip': {'valueSuffix': ' '+unit,
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
               'data': pts}
        if ser.type == 'scatter':
            sop['tooltip'] = {'headerFormat': '<small>{point.key}</small><br/><table>',
                              'pointFormat': '<tr><td style="color:{series.color}">{series.name}</td>\
                                <td style = "text-align: right">: <b>{point.y}</b></td></tr>'}
        allseries.append(sop)
        options['series'] = allseries
        jop = json.dumps(options,default=date_handler)
        # remove quotes around date stuff
        jop = re.sub(r'\"(Date\.UTC\([\d,]+\))\"',r'\1', jop)
        context['options'] = jop
        context['theme'] = ' None' #ser.theme()
        return context

class ChartBaseView(TemplateView):
    template_name = 'data/plain_chart.html'

    def get_json(self, chart):
        options = {
            'rangeSelector': { 'enabled': True,
                              'inputEnabled': True,
                              'selected': 5,
                              },
#            'navigator': {'adaptToUpdatedData': False, 'enabled': False},
#             'loading': {'style': {'backgroundColor': 'white', 'fontFamily': 'Arial', 'fontSize': 'small'},
#                         'labelStyle': {'fontWeight': 'normal'},
#                         'hideDuration': 0,
#                         },
            'chart': {'animation': False, 
                      'zoomType': 'x',
                      'events': {'load': None},
                      },
            'title': {'text': chart.title},
            'xAxis': {'type': 'datetime'},
            'yAxis': [],
            'tooltip': {'valueDecimals': 2,
                        'shared': True,
                       }, 
            'legend': {'enabled': chart.series.count() > 1},
            'plotOptions': {'line': {'marker': {'enabled': False}},
                            'column': {'allowpointSelect': True, 'pointPadding': 0.01, 'groupPadding': 0.01, 'pointPlacement': 'between'}},            
            'credits': {'enabled': True, 
                        'text': 'acaciawater.com', 
                        'href': 'http://www.acaciawater.com',
                       }
            }

        start = chart.auto_start()
        options['xAxis']['min'] = tojs(start)
#         if not chart.stop is None:
#             options['xAxis']['max'] = tojs(chart.stop)
        allseries = []
        for _,s in enumerate(chart.series.all()):
            ser = s.series
            title = s.label #ser.name if len(ser.unit)==0 else '%s [%s]' % (ser.name, ser.unit) if chart.series.count()>1 else ser.unit
            options['yAxis'].append({
                                     'title': {'text': title},
                                     'opposite': 0 if s.axislr == 'l' else 1,
                                     'min': s.y0,
                                     'max': s.y1
                                     })
            pts = [] #[[p.date,p.value] for p in ser.datapoints.filter(date__gte=start).order_by('date')]
            name = s.name
            if name is None or name == '':
                name = ser.name
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
            if s.type == 'column' and s.stack is not None:
                sop['stacking'] = s.stack
            allseries.append(sop)
        options['series'] = allseries
        jop = json.dumps(options,default=date_handler)
        # remove quotes around date stuff
        jop = re.sub(r'\"(Date\.UTC\([\d,]+\))\"',r'\1', jop)
        return jop
    
    def get_context_data(self, **kwargs):
        context = super(ChartBaseView, self).get_context_data(**kwargs)
        pk = context.get('pk',1)
        chart = Chart.objects.get(pk=pk)
        jop = self.get_json(chart)
        context['options'] = jop
        context['chart'] = chart
        return context
        
class ChartView(ChartBaseView):
    template_name = 'data/chart_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ChartView, self).get_context_data(**kwargs)
        pk = context.get('pk',1)
        if pk is not None:
            chart = Chart.objects.get(pk=pk)
            jop = self.get_json(chart)
            context['options'] = jop
            context['chart'] = chart
        return context
    
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
