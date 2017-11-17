'''
Created on Jun 3, 2014

@author: theo
'''
from django.views.generic import DetailView, FormView, TemplateView
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.core.files.storage import default_storage
from django.conf import settings
from django.contrib.auth.decorators import login_required
import numpy as np
import pandas as pd

from .models import Network, Well, Screen
from .forms import UploadFileForm
from .actions import download_well_nitg

import os, json, logging, time

from util import handle_uploaded_files
from django.utils.timezone import get_current_timezone

logger = logging.getLogger(__name__)

class WellView(DetailView):
    template = 'meetnet/well_info.html'
    model = Well

    def get_context_data(self, **kwargs):
        context = super(WellView, self).get_context_data(**kwargs)
        well = self.get_object()
        context['chart'] = well.chart.url if well.chart.name else None
        return context

class ScreenView(DetailView):
    model = Screen
    
    def get_context_data(self, **kwargs):
        context = super(ScreenView, self).get_context_data(**kwargs)
        screen = self.get_object()
        context['chart'] = screen.chart.url if screen.chart.name else None 
        return context

def wellinfo(request, pk):
    ''' return contents of info window for google maps '''
    well = Well.objects.get(pk=pk)
    contents = render_to_string('meetnet/well_info.html', {'object': well})
    return HttpResponse(contents, content_type = 'application/text')

class NetworkView(DetailView):
    model = Network
    
    def get_context_data(self, **kwargs):
        context = super(NetworkView, self).get_context_data(**kwargs)
        network = self.get_object()
        content = []
        if network:
            if not network.bound is None:
                context['boundary'] = network.bound
            for well in network.well_set.all():
                pos = well.latlon()
                content.append({'network': network.id,
                                'well': well.id,
                                'name': well.name,
                                'nitg': well.nitg,
                                'lat': pos.y,
                                'lon': pos.x,
                                'url': reverse('meetnet:well-info', args=[well.id]),
                                })
        context['content'] = json.dumps(content) if content else None
        context['maptype'] = 'ROADMAP'
        context['apikey'] = settings.GOOGLE_MAPS_API_KEY
        return context
        
class ScreenChartView(TemplateView):
    template_name = 'plain_chart.html'
    
    def get_context_data(self, **kwargs):
        context = super(ScreenChartView, self).get_context_data(**kwargs)
        filt = Screen.objects.get(pk=context['pk'])
        name = unicode(filt)
        data = filt.get_levels(ref='nap')
        options = {
            'chart': {'type': 'line', 'animation': False, 'zoomType': 'x'},
            'title': {'text': name},
            'xAxis': {'type': 'datetime'},
            'yAxis': [{'title': {'text': 'm'}}
                      ],
            'tooltip': {'valueSuffix': ' m tov NAP',
                        'valueDecimals': 2,
                        'shared': True,
                       }, 
            'legend': {'enabled': False},
            'plotOptions': {'line': {'marker': {'enabled': False}}},            
            'credits': {'enabled': True, 
                        'text': 'acaciawater.com', 
                        'href': 'http://www.acaciawater.com',
                       },
            'series': [{'name': name,
                        'type': 'line',
                        'data': data
                        },
                       ]
            }
            
        context['options'] = json.dumps(options, default=lambda x: int(time.mktime(x.timetuple())*1000))
        context['screen'] = filt
        return context

def json_series(request, pk):
    screen = get_object_or_404(Screen,pk=pk)
    what = request.GET.get('mode','comp') # choices: comp, hand
    if what == 'comp':
        series = screen.get_compensated_series()
    elif what == 'hand':
        series = screen.get_manual_series()
    else:
        raise 'Illegal series type requested'
    
    ref = request.GET.get('ref','nap') # choices: nap, bkb, mv, cm
    if ref == 'nap':
        pass
    elif ref =='bkb':
        series = screen.refpnt - series
    elif ref == 'mv':
        series = screen.well.maaiveld - series
    elif ref == 'cm':
        # converteren naar cm boven sensor
        depths = screen.loggerpos_set.order_by('start_date').values_list('start_date','depth')
        if len(depths)>0:
            x,y = zip(*depths)
            nap = (screen.refpnt - pd.Series(index = x, data = y))
            nap = nap.reindex(series.index,method='pad')
            series = (series - nap) * 100
        else:
            series = pd.Series()
    if series is None or series.empty:
        values = []
    else:
        values = zip(series.index, series.values)
        #values = zip(series.index.astype(np.int64)//10**6, series.values)
    data = {'screen%s'%screen.nr: values}
    return HttpResponse(json.dumps(data,default=lambda x: int(time.mktime(x.timetuple())*1000)),content_type='application/json')
    #return HttpResponse(json.dumps(data),content_type='application/json')
    
class WellChartView(TemplateView):
    template_name = 'meetnet/chart_detail.html'
        
    def get_context_data(self, **kwargs):
        context = super(WellChartView, self).get_context_data(**kwargs)
        well = Well.objects.get(pk=context['pk'])
        name = unicode(well)
         
        options = {
             'rangeSelector': { 'enabled': True,
                               'inputEnabled': True,
                               },
            'navigator': {'adaptToUpdatedData': True, 'enabled': True},
            'chart': {'type': 'arearange', 'zoomType': 'x','events':{'load':None}},
            'title': {'text': name},
            'xAxis': {'type': 'datetime'},
            'yAxis': [{'title': {'text': 'Grondwaterstand\n(m tov NAP)'}}
                      ],
            'tooltip': {'valueSuffix': ' m',
                        'valueDecimals': 2,
                        'shared': True,
                       }, 
            'legend': {'enabled': True},
            'plotOptions': {'line': {'marker': {'enabled': False}}},            
            'credits': {'enabled': True, 
                        'text': 'acaciawater.com', 
                        'href': 'http://www.acaciawater.com',
                       },
            }

        series = []
        xydata = []
        start = stop = None

        for screen in well.screen_set.all():
            if screen.has_data():
                xydata = None
                series.append({'name': 'filter {}'.format(screen.nr),
                            'type': 'line',
                            'data': xydata,
                            'lineWidth': 1,
                            'zIndex': 2,
                            'id': 'screen%d' % screen.nr
                            })
                if start:
                    start = min(start,screen.start())
                else:
                    start = screen.start()
                    
                if stop:
                    stop = min(stop,screen.stop())
                else:
                    stop = screen.stop()

            # sensor positie tov NAP
#             data = []
#             depths = screen.loggerpos_set.order_by('start_date').values_list('start_date','depth')
#             if len(depths)>0:
#                 last = None
#                 for date,value in depths:
#                     if last:
#                         data.append((date,last))
#                     value = screen.refpnt - value
#                     data.append((date,value))
#                     last = value
# #                 date = datetime.datetime(2017,2,1)
# #                 last_date = int(time.mktime(date.timetuple())*1000)
# #                 data.append((last_date,last))
#             if data:
#                 series.append({'name': 'diver {}'.format(screen.nr),
#                         'type': 'line',
#                         'data': data,
#                         'zIndex': 1,
#                         'id': 'diver%d' % screen.nr
#                         })
            

            data = screen.get_manual_series()
            if data is None:
                continue
            hand = zip(data.index.to_pydatetime(), data.values)
            series.append({'name': 'peiling {}'.format(screen.nr),
                        'type': 'scatter',
                        'data': hand,
                        'zIndex': 3,
                        'marker': {'symbol': 'circle', 'radius': 6, 'lineColor': 'white', 'lineWidth': 2, },#'fillColor': screencolor(screen)},
                        'tooltip': {
                                'headerFormat': '<span style="font-size:10px">{point.x:%A %e %B %Y %H:%k }</span><br/><table>',
                                'pointFormat': '<tr><td style="color:{series.color};padding:0;font-size:11px;">{series.name}: </td><td style="padding:0"><b>{point.y:,.2f}</b></td></tr>',
                                'useHTML': True
                            },
                        })
            

        if well.maaiveld and start and stop:
            tz = get_current_timezone()
            series.append({'name': 'maaiveld',
                        'type': 'line',
                        'lineWidth': 2,
                        'color': '#009900',
                        'dashStyle': 'Dash',
                        'data': [(start.astimezone(tz),well.maaiveld),(stop.astimezone(tz),well.maaiveld)],
                        'zIndex': 4,
                        })

        # neerslag toevoegen
        if hasattr(well,'meteo'):
            neerslag = well.meteo.neerslag
            if neerslag:
                data = neerslag.to_pandas(start=xydata[0][0], stop=xydata[-1][0]) / 10.0 # 0.1 mm -> mm
                if not data.empty:
                    data = zip(data.index.to_pydatetime(), data.values)
                    series.append({'name': 'Neerslag '+ neerslag.datasource.name,
                                'type': 'column',
                                'data': data,
                                'yAxis': 1,
                                'pointRange': 24 * 3600 * 1000, # 1 day
                                'pointPadding': 0.01,
                                'pointPlacement': 0.5,
                                'zIndex': 1,
                                'color': 'orange', 
                                'borderColor': '#cc6600', 
                                })
                    options['yAxis'].append({'title': {'text': 'Neerslag (mm)'},
                                             'opposite': 1,
                                             'min': 0,
                                             })
        options['series'] = series
        context['options'] = json.dumps(options, default=lambda x: int(time.mktime(x.timetuple())*1000))
        context['object'] = well
        return context

from acacia.data.views import DownloadSeriesAsZip
from acacia.data.models import Series

def get_series(screen):
    name = '%s COMP' % unicode(screen)
    try:
        return Series.objects.get(name=name)
    except:
        return None

@login_required
def DownloadSeriesAsNITG(request,source,series):
    ''' Tijdreeksen downloaden als zip file '''
    download_well_nitg(None, request, series) # reuse method from admin.actions. Runs in separate thread
    return redirect(request.META.get('HTTP_REFERER','/'))

def EmailNetworkSeries(request,pk):
    net = get_object_or_404(Network, pk=pk)
    series = [get_series(s) for w in net.well_set.all() for s in w.screen_set.all()]
    return DownloadSeriesAsZip(request, unicode(net), series)

def EmailNetworkNITG(request, pk):
    net = get_object_or_404(Network, pk=pk)
    return DownloadSeriesAsNITG(request, unicode(net), net.well_set.all())
    
def EmailWellSeries(request,pk):
    well = get_object_or_404(Well, pk=pk)
    series = [get_series(s) for s in well.screen_set.all()]
    return DownloadSeriesAsZip(request, unicode(well), series)
    
def EmailScreenSeries(request,pk):
    screen = get_object_or_404(Screen,pk=pk)
    series = get_series(screen)
    return DownloadSeriesAsZip(request, unicode(screen), series)

class UploadDoneView(TemplateView):
    template_name = 'upload_done.html'

    def get_context_data(self, **kwargs):
        context = super(UploadDoneView, self).get_context_data(**kwargs)
        context['user'] = self.request.user
        context['network'] = get_object_or_404(Network,pk=int(kwargs.get('id',1)))
        return context

def save_file(file_obj,folder):
    path = default_storage.path(os.path.join(folder,file_obj.name))
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    with open(path, 'wb') as destination:
        for chunk in file_obj.chunks():
            destination.write(chunk)
    return path

class UploadFileView(FormView):

    template_name = 'upload.html'
    form_class = UploadFileForm
    success_url = '/done/1'
    
    def get_success_url(self):
        return reverse('meetnet:upload_done',kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        context = super(UploadFileView, self).get_context_data(**kwargs)
        context['network'] = get_object_or_404(Network,pk=int(self.kwargs.get('id')))
        return context

    def form_valid(self, form):

        # download files to upload folder
        local_files = []
        for f in form.files.getlist('filename'):
            path = save_file(f,'upload')
            local_files.append(path)
            
        network = get_object_or_404(Network,pk=int(self.kwargs.get('id')))

        # start background process that handles uploaded files
        from threading import Thread
        t = Thread(target=handle_uploaded_files, args=(self.request, network, local_files))
        t.start()
        
        return super(UploadFileView,self).form_valid(form)

