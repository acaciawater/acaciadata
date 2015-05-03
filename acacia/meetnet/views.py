'''
Created on Jun 3, 2014

@author: theo
'''
from django.views.generic import DetailView, TemplateView
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from models import Network, Well, Screen
import json, logging, datetime, time
import pandas as pd

logger = logging.getLogger(__name__)

class WellView(DetailView):
    template = 'well_info.html'
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
    contents = render_to_string('well_info.html', {'object': well})
    return HttpResponse(contents, content_type = 'application/text')

class NetworkView(DetailView):
    model = Network
    
    def get_context_data(self, **kwargs):
        context = super(NetworkView, self).get_context_data(**kwargs)
        network = self.get_object()
        content = []
        for well in network.well_set.all():
            pos = well.latlon()
            content.append({'network': network.id,
                            'well': well.id,
                            'name': well.name,
                            'lat': pos.y,
                            'lon': pos.x,
                            'url': reverse('well-info', args=[well.id]),
                            })
        context['content'] = json.dumps(content)
        if not network.bound is None:
            context['boundary'] = network.bound
        context['maptype'] = 'HYBRID'
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

class WellChartView(TemplateView):
    template_name = 'plain_chart.html'
    
    def get_context_data(self, **kwargs):
        context = super(WellChartView, self).get_context_data(**kwargs)
        well = Well.objects.get(pk=context['pk'])
        name = unicode(well)
        options = {
             'rangeSelector': { 'enabled': True,
                               'inputEnabled': True,
                               },
            'navigator': {'adaptToUpdatedData': True, 'enabled': True},
            'chart': {'type': 'arearange', 'zoomType': 'x'},
            'title': {'text': name},
            'xAxis': {'type': 'datetime'},
            'yAxis': [{'title': {'text': 'm tov NAP'}}
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
        start = datetime.datetime(2014,1,1)
        stop = datetime.datetime(2015,1,1)
        for screen in well.screen_set.all():
            name = unicode(screen)
            data = screen.to_pandas(ref='nap')[start:stop]
            xydata = zip(data.index.to_pydatetime(), data.values)
            series.append({'name': name,
                        'type': 'line',
                        'data': xydata,
                        'lineWidth': 1,
                        'zIndex': 1,
                        })
            mean = pd.expanding_mean(data)
#             series.append({'name': 'gemiddelde',
#                         'type': 'line',
#                         'data': zip(mean.index.to_pydatetime(), mean.values),
#                         'linkedTo' : ':previous',
#                         })
            std = pd.expanding_std(data)
            a = (mean - std).dropna()
            b = (mean + std).dropna()
            ranges = zip(a.index.to_pydatetime(), a.values, b.values)
            series.append({'name': 'spreiding',
                        'data': ranges,
                        'type': 'arearange',
                        'lineWidth': 0,
                        'fillOpacity': 0.2,
                        'linkedTo' : ':previous',
                        'zIndex': 0,
                        })
            data = screen.to_pandas(ref='nap',kind='HAND')[start:stop]
            hand = zip(data.index.to_pydatetime(), data.values)
            series.append({'name': 'handpeiling',
                        'type': 'scatter',
                        'data': hand,
                        'zIndex': 2,
                        'marker': {'symbol': 'circle', 'radius': 6, 'lineColor': 'white', 'lineWidth': 2, 'fillColor': 'blue'},
                        })

        if len(xydata)>0:
            mv = []
            for i in range(len(xydata)):
                mv.append((xydata[i][0], screen.well.maaiveld))
            series.append({'name': 'maaiveld',
                        'type': 'line',
                        'lineWidth': 1,
                        'dashStyle': 'Dash',
                        'color': 'white',
                        'data': mv
                        })
        
        options['series'] = series
        context['options'] = json.dumps(options, default=lambda x: int(time.mktime(x.timetuple())*1000))
        context['object'] = well
        return context
