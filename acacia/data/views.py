from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.shortcuts import get_object_or_404
from models import Project, ProjectLocatie, DataFile, Chart, Dashboard
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

class ProjectView(DetailView):
    model = Project       
    
class ProjectListView(ListView):
    model = Project

class ProjectLocatieListView(ListView):
    model = ProjectLocatie

    def get_context_data(self, **kwargs):
        context = super(ProjectLocatieListView, self).get_context_data(**kwargs)
        context['project'] = self.project
        return context

    def get_queryset(self,**kwargs):
        self.project = get_object_or_404(Project,name__iexact=self.args[0])
        return ProjectLocatie.objects.filter(project=self.project)
        
def tojs(d):
    return 'Date.UTC(%d,%d,%d,%d,%d,%d)' % (d.year, d.month-1, d.day, d.hour, d.minute, d.second)

def date_handler(obj):
    return tojs(obj) if isinstance(obj, datetime.date) or isinstance(obj, datetime.datetime) else obj

class ChartView(TemplateView):
    template_name = 'data/plain_chart.html'

    def get_context_data(self, **kwargs):
        context = super(ChartView, self).get_context_data(**kwargs)
        pk = context.get('pk',1)
        chart = Chart.objects.get(pk=pk)
        options = {
            'chart': {'type': chart.type, 'animation': False},
            'title': {'text': chart.title},
            'xAxis': {'type': 'datetime'},
            'yAxis': [],
            'legend': {'enabled': chart.series.count() > 1},
            'plotOptions': {'line': {'marker': {'enabled': False}}},            
            'credits': {'enabled': True, 'text': 'acaciawater.com', 'href': 'http://www.acaciawater.com'}
            }

        allseries = []
        for i,ser in enumerate(chart.series.all()):
            title = ser.name if len(ser.unit)==0 else '%s [%s]' % (ser.name, ser.unit)
            options['yAxis'].append({
                                     'title': {'text': title},
                                     'opposite': 0 if i % 2 == 0 else 1
                                     })
            pts = [[p.date,p.value] for p in ser.datapoints.all().order_by('date')]
            allseries.append({
                              'name': ser.name,
                              'type': ser.type,
                              'yAxis': i,
                              'data': pts})
        options['series'] = allseries
        jop = json.dumps(options,default=date_handler)
        # remove quotes around date stuff
        jop = re.sub(r'\"(Date\.UTC\([\d,]+\))\"',r'\1', jop)
        context['options'] = jop
        return context

class DashView(TemplateView):
    template_name = 'data/dash.html'
    
    def get_context_data(self, **kwargs):
        context = super(DashView,self).get_context_data(**kwargs)
        slug = context.get('slug', 'None')
        dash = get_object_or_404(Dashboard, slug=slug)
        context['dashboard'] = dash
        return context