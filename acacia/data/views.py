from django.views.generic.edit import CreateView
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from models import DataFile, Chart, Series
import pandas as pd
import numpy as np
import json
import datetime
import re

import logging
logger = logging.getLogger(__name__)

class DataFileAddView(CreateView):
    model = DataFile
    fields = ['file', ]

class DataFileDetailView(DetailView):
    model = DataFile

def tojs(d):
    return 'Date.UTC(%d,%d,%d)' % (d.year, d.month, d.day)

def date_handler(obj):
    return tojs(obj) if isinstance(obj, datetime.date) or isinstance(obj, datetime.datetime) else obj

class ChartView(TemplateView):
    template_name = 'data/highchart.html'

    def get_context_data(self, **kwargs):
        context = super(ChartView, self).get_context_data(**kwargs)
        chart = Chart.objects.get(pk=1)
        options = {
            'chart': {'type': chart.type, 'animation': False},
            'title': {'text': chart.title},
            'xAxis': {'type': 'datetime'},
            'yAxis': [],
            'legend': {'enabled': False},
            'plotOptions': {'line': {'marker': {'enabled': False}}}            
            }

        allseries = []
        for i,ser in enumerate(chart.series.all()):
            options['yAxis'].append({
                                     'title': {'text': ser.name},
                                     'opposite': 0 if i % 2 == 0 else 1
                                     })
            pts = [[p.date,p.value] for p in ser.datapoints.all()]
            allseries.append({
                              'name': ser.name,
                              'type': ser.type,
                              'yAxis': i,
                              'data': pts})
        options['series'] = allseries
        jop = json.dumps(options,default=date_handler)
        jop = re.sub(r'\"(Date\.UTC\(\d{4},\d+,\d+\))\"',r'\1', jop)
        context['options'] = jop
        return context

    def get_context_data1(self, **kwargs):
        context = super(ChartView, self).get_context_data(**kwargs)
        length = 36
        ts = pd.Series(np.random.randn(length), index = pd.date_range('1/1/1960', periods = length))
        ts = ts.cumsum()
        options = {
            'chart': {'type': 'column', 'animation': False},
            'title': {'text': 'Neerslag Louwersoog'},
            'subtitle': {'text': 'Dit zijn fictieve data'},
            'xAxis': {'type': 'datetime'},
            'yAxis': {'title': {'text': 'Neerslag [mm/10]'}},
            'legend': {'enabled': False},
            'plotOptions': {'line': {'marker': {'enabled': False}}}            
            }
            
        options['series'] = [{'name': 'name','data': [[d,v] for d,v in ts.iteritems()]}]
        jop = json.dumps(options,default=date_handler)
        # remove quotes around date stuff
        jop = re.sub(r'\"(Date\.UTC\(\d{4},\d+,\d+\))\"',r'\1', jop)
        context['options'] = jop
        return context
    
        