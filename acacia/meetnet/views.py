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
import pandas as pd

from .models import Network, Well, Screen
from .forms import UploadFileForm
from .actions import download_well_nitg

import os, logging
import simplejson as json

from util import handle_uploaded_files
from django.utils.timezone import get_current_timezone
from django.utils.text import slugify
from acacia.data.actions import download_series_csv
from acacia.data.util import series_as_csv, unix_timestamp
from acacia.validation.models import RollingRule, RangeRule

logger = logging.getLogger(__name__)

class NavMixin(object):
    """ Mixin for browsing through devices sorted by name """

    def nav(self,well):
        nxt = Well.objects.filter(name__gt=well.name)
        nxt = nxt.first() if nxt else None
        prv = Well.objects.filter(name__lt=well.name)
        prv = prv.last() if prv else None
        return {'next': nxt, 'prev': prv}

class WellView(NavMixin, DetailView):
    #template = 'meetnet/well_info.html'
    model = Well

    def get_context_data(self, **kwargs):
        context = super(WellView, self).get_context_data(**kwargs)
        well = self.get_object()
        context['chart'] = well.chart.url if well.chart.name else None
        context['nav'] = self.nav(well)
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
            
        context['options'] = json.dumps(options, default=lambda x: int(unix_timestamp(x)*1000))
        context['screen'] = filt
        return context

def json_series(request, pk):
    screen = get_object_or_404(Screen,pk=pk)
    what = request.GET.get('mode','comp') # choices: comp, hand
    ref = request.GET.get('ref','nap') # choices: nap, bkb, mv, cm
#     filters = [
#         RangeRule(name = 'range', lower = -5, upper = 5),
#         RollingRule(name = 'spike', count = 3, tolerance = 3, comp ='LT')
#         ]
    series = screen.get_series(ref,what,rule='H')#,filters=filters)
    if series is None or series.empty:
        values = []
    else:
        values = zip(series.index, series.values)
        
    data = {'screen%s'%screen.nr: values}
    stats = request.GET.get('stats','0')
    try:
        stats = int(stats)
        if stats:
            mean = pd.expanding_mean(series)
            std = pd.expanding_std(series)
            a = (mean - std).dropna()
            b = (mean + std).dropna()
            ranges = zip(a.index.to_pydatetime(), a.values, b.values)
            data.update({'stats%s'%screen.nr: ranges})
    except:
        pass
    return HttpResponse(json.dumps(data,ignore_nan=True,default=lambda x: int(unix_timestamp(x)*1000)),content_type='application/json')
    
class WellChartView(NavMixin, TemplateView):
    template_name = 'meetnet/chart_detail.html'
        
    def get_context_data(self, **kwargs):
        context = super(WellChartView, self).get_context_data(**kwargs)
        well = Well.objects.get(pk=context['pk'])
        
        context['object'] = well
        context['nav'] = self.nav(well)

        if not well.nitg:
            title = well.name
        elif not well.name:
            title = well.nitg
        elif well.name == well.nitg:
            title = well.name
        else:
            title = '{name} ({nitg})'.format(name=well.name, nitg=well.nitg)
        
        options = {
             'rangeSelector': { 'enabled': True,
                               'inputEnabled': True,
                               },
            'navigator': {'adaptToUpdatedData': True, 'enabled': True},
            'chart': {'zoomType': 'x','events':{'load':None}},
            'title': {'text': title},
            'xAxis': {'type': 'datetime'},
            'yAxis': [{'title': {'text': 'Grondwaterstand\n(m tov NAP)'}}
                      ],
            'tooltip': {'valueSuffix': ' m',
                        'valueDecimals': 2,
                        'shared': True,
                       }, 
            'legend': {'enabled': True},
            'plotOptions': {'line': {'marker': {'enabled': False}}, 'series': {'connectNulls': False}},
            'credits': {'enabled': True, 
                        'text': 'acaciawater.com', 
                        'href': 'http://www.acaciawater.com',
                       },
            }

        series = []
        start = stop = None

        for screen in well.screen_set.all():
            if screen.has_data():
                series.append({'name': 'filter {}'.format(screen.nr),
                            'type': 'line',
                            'data': [],
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

                # add statistics if requested
                stats = self.request.GET.get('stats','0')
                stats = int(stats)
                if stats:
                    series.append({'name': 'spreiding %d'% screen.nr,
                            'id': 'stats%d' % screen.nr,
                            'data': [],
                            'type': 'arearange',
                            'lineWidth': 0,
                            'linkedTo': ':previous',
                            #'color': '#0066FF',
                            'fillOpacity': 0.2,
                            'zIndex': 0,
                            'marker': {'enabled':False}
                            })

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
                                'headerFormat': '<span style="font-size:10px">{point.x:%A %e %B %Y %H:%M }</span><br/><table>',
                                'pointFormat': '<tr><td style="color:{series.color};padding:0;font-size:11px;">{series.name}: </td><td style="padding:0"><b>{point.y:,.2f}</b></td></tr>',
                                'useHTML': True
                            },
                        })
            

        maaiveld = well.maaiveld or well.ahn
        if maaiveld and start and stop:
            tz = get_current_timezone()
            maaiveld = float(maaiveld)
            series.append({'name': 'maaiveld',
                        'type': 'line',
                        'lineWidth': 2,
                        'color': '#009900',
                        'dashStyle': 'Dash',
                        'data': [(start.astimezone(tz),maaiveld),(stop.astimezone(tz),maaiveld)],
                        'zIndex': 4,
                        })

        # neerslag toevoegen
        if hasattr(well,'meteo'):
            neerslag = well.meteo.neerslag
            if neerslag:
                data = neerslag.to_array(start=start, stop=stop)
                if data:
                    aantal = len(data)
                    if aantal>1:
                        first = data[0][0]
                        last = data[-1][0]
                        deltat = (last - first)
                        secs = deltat.total_seconds() / (aantal-1)
                        hours = max(int(secs/3600),1)
                    else:
                        hours = 1 
                    
                    series.append({'name': neerslag.name,
                                'type': 'column',
                                'data': data,
                                'yAxis': 1,
                                'pointRange': hours * 3600 * 1000, 
                                'pointPadding': 0,
                                'groupPadding': 0,
                                'pointPlacement': 0.5,
                                'zIndex': 1,
                                'color': 'orange', 
                                'borderColor': '#cc6600', 
                                'tooltip': {'valueSuffix': ' '+neerslag.unit,
                                            'valueDecimals': 2,
                                            'shared': True,
                                           }, 
                                })
                    options['yAxis'].append({'title': {'text': 'Neerslag ({})'.format(neerslag.unit)},
                                             'opposite': 1,
                                             'min': 0,
                                             })
        options['series'] = series
        
        context['options'] = json.dumps(options, default=lambda x: unix_timestamp(x)*1000)
        return context

from acacia.data.views import DownloadSeriesAsZip

def get_series(screen):
    return screen.find_series()

def filter_wells(network,request):    
    from django.db.models import Q
    query = network.well_set.all()
    term = request.GET.get('search')
    if term:
        query = query.filter(
            Q(straat__icontains=term)|
            Q(postcode__icontains=term)|
            Q(plaats__icontains=term)|
            Q(name__icontains=term)|
            Q(nitg__icontains=term))
    aquifer = request.GET.get('aquifer')
    if aquifer and aquifer != 'all':
        ids = Screen.objects.filter(aquifer__iexact=aquifer).values_list('well__id')
        query = query.filter(id__in=ids)
    return query

def filter_screens(well,request):    
    query = well.screen_set.all()
    aquifer = request.GET.get('aquifer')
    if aquifer and aquifer != 'all':
        query = query.filter(aquifer__iexact=aquifer)
    return query

@login_required
def DownloadSeriesAsNITG(request,source,series):
    ''' Tijdreeksen downloaden als zip file '''
    download_well_nitg(None, request, series) # reuse method from admin.actions. Runs in separate thread
    return redirect(request.META.get('HTTP_REFERER','/'))

@login_required
def EmailNetworkSeries(request,pk):
    net = get_object_or_404(Network, pk=pk)
    series = [get_series(s) for w in filter_wells(net,request) for s in filter_screens(w, request)]
    return DownloadSeriesAsZip(request, unicode(net), filter(lambda x: x, series))

@login_required
def EmailNetworkNITG(request, pk):
    net = get_object_or_404(Network, pk=pk)
    return DownloadSeriesAsNITG(request, unicode(net), filter_wells(net, request))
    
@login_required
def EmailWellSeries(request,pk):
    well = get_object_or_404(Well, pk=pk)
    series = [get_series(s) for s in filter_screens(well, request)]
    return DownloadSeriesAsZip(request, unicode(well), filter(lambda x:x, series))

@login_required
def DownloadWellSeries(request,pk):
    well = get_object_or_404(Well, pk=pk)
    series = [get_series(s) for s in filter_screens(well, request)]
    series = filter(lambda x:x, series)
    if series:
        if len(series)==1:
            resp = series_as_csv(series[0]) # one single csv file
            resp['Content-Disposition'] = 'attachment; filename={}.csv'.format(slugify(str(well)))
        else:
            resp = download_series_csv(None,request,series) # zip archive with all series
            resp['Content-Disposition'] = 'attachment; filename={}.zip'.format(slugify(str(well)))
        return resp
    
@login_required
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

