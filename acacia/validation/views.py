import os, tempfile, json, re
import time
import pandas as pd
import numpy as np

from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.files.storage import default_storage
from django.views.generic import FormView, TemplateView, DetailView
from django.views.decorators.gzip import gzip_page
from django.http.response import HttpResponse
from django.core.urlresolvers import reverse

from acacia.validation.models import Validation, Result
from acacia.data.util import slugify
from acacia.validation.forms import UploadFileForm, ValidationForm
from acacia.data.views import SeriesView, date_handler

import logging
logger = logging.getLogger(__name__)

def download(request, pk):
    ''' download Excel file for validation '''
    validation = get_object_or_404(Validation,pk=pk)
    
    pts = [(p.date,p.value) for p in validation.series.datapoints.all()]
    index,data = zip(*pts)
    raw = pd.Series(data,index)

    pts = [(p.date,p.value) for p in validation.validpoint_set.all()]
    index,data = zip(*pts)
    val = pd.Series(data,index)
        
    # build dataframe with both raw and validated time series
    df = pd.DataFrame({'raw': raw, 'validated': val})

    # create (and delete) tmp file and remember filename
    if not os.path.exists(settings.EXPORT_ROOT):
        os.mkdir(settings.EXPORT_ROOT)
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.xlsx', dir=settings.EXPORT_ROOT) as tmp:
        xlfile = tmp.name

    # export dataframe to excel
    df.to_excel(xlfile)

    # read excel file we've just created
    with open(xlfile,"rb") as x:
        xldata = x.read()
        
    response = HttpResponse(xldata,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=%s' % slugify(validation.series)+'.xlsx'
    return response

class UploadDoneView(TemplateView):
    template_name = 'upload_done.html'

    def get_context_data(self, **kwargs):
        context = super(UploadDoneView, self).get_context_data(**kwargs)
        context['user'] = self.request.user
        context['next'] = self.request.GET.get('next', self.request.get_full_path())
        return context

def save_file(file_obj,folder):
    path = default_storage.path(os.path.join(folder,file_obj.name))
    fldr = os.path.dirname(path)
    if not os.path.exists(fldr):
        os.makedirs(fldr)
    with open(path, 'wb') as destination:
        for chunk in file_obj.chunks():
            destination.write(chunk)
    return path

class UploadFileView(FormView):

    template_name = 'upload.html'
    form_class = UploadFileForm
    success_url = 'up/1/done'
    
    def get_success_url(self):
#        return self.success_url
        url = reverse('validation:upload_done',kwargs=self.kwargs)
        return url + '?next=' + self.request.get_full_path()

    def get_context_data(self, **kwargs):
        context = super(UploadFileView, self).get_context_data(**kwargs)
        context['validation'] = get_object_or_404(Validation,pk=int(self.kwargs.get('pk')))
        return context

    def form_valid(self, form):

        # download files to upload folder
        local_files = []
        for f in form.files.getlist('filename'):
            path = save_file(f,'upload')
            local_files.append(path)
            
        # start background process that handles uploaded files
#         from threading import Thread
#         t = Thread(target=handle_uploaded_files, args=(self.request, network, local_files))
#         t.start()
        
        return super(UploadFileView,self).form_valid(form)


class ValidationView(FormView):
     
    template_name = 'validation.html'
    form_class = ValidationForm
    success_url = 'val/1/done'
      
    def get_success_url(self):
        return reverse('validation:validation_done',kwargs=self.kwargs)
  
    def get_context_data(self, **kwargs):
        context = super(ValidationView, self).get_context_data(**kwargs)
        val = get_object_or_404(Validation,pk=int(self.kwargs.get('pk')))
        context['validation'] = val
        context['invalid'] = val.invalid_points.count()
        context['next'] = self.request.get_full_path()
        return context
  
    def form_valid(self, form):
        return super(ValidationView,self).form_valid(form)
      

@gzip_page
def ValToJson(request, pk):
    ''' return two series: raw and validated '''
    validation = get_object_or_404(Validation,pk=pk)
    options = {'start': request.GET.get('start', None),
               'stop': request.GET.get('stop', None)}
    val = validation.to_pandas(**options)
    raw = validation.series.to_pandas(**options)
    df = pd.DataFrame({'raw':raw,'validated': val})
    def nn(x):
        # replace NaN with None for json converter
        return None if np.isnan(x) else x
    pts = [(r[0],nn(r[1][0]),nn(r[1][1])) for r in df.iterrows()]
    j = json.dumps(pts, default=lambda x: time.mktime(x.timetuple())*1000.0)
    return HttpResponse(j, content_type='application/json')
    
class SeriesView(DetailView):
    model = Validation
    
    def get_context_data(self, **kwargs):
        context = super(SeriesView, self).get_context_data(**kwargs)
        val = self.get_object()
        ser = val.series
        unit = ser.unit
        title = unit or ser.name
        options = {
            'rangeSelector': { 'enabled': False,
                              'inputEnabled': False,
                              },
            'navigator': {'adaptToUpdatedData': True, 'enabled': False},
            'loading': {'style': {'backgroundColor': 'white', 'fontFamily': 'Arial', 'fontSize': 'small'},
                        'labelStyle': {'fontWeight': 'normal'},
                        'hideDuration': 0,
                        },
            'chart': {'type': ser.type, 
                      'animation': False, 
                      'zoomType': 'x',
                      'events': {'load': None},
                      },
            'title': {'text': ser.name},
            'xAxis': {'type': 'datetime', 'events': {}},
            'yAxis': [{'title': {'text': title}}],
            'tooltip': {'valueSuffix': ' '+(unit or ''),
                        'valueDecimals': 2,
                        'shared' : True,
                       }, 
            'plotOptions': {'line': {'marker': {'enabled': False}}},            
            'credits': {'enabled': True, 
                        'text': 'acaciawater.com', 
                        'href': 'http://www.acaciawater.com',
                       }
            }
           
        series = [{'name': 'raw', 'type': ser.type, 'data': [], 'color': 'red' },
                {'name': 'validated', 'type': ser.type, 'data': [], 'color': 'green' } ]                 

        options['series'] = series
        jop = json.dumps(options,default=date_handler)
        # remove quotes around date stuff
        jop = re.sub(r'\"(Date\.UTC\([\d,]+\))\"',r'\1', jop)

        context['options'] = jop
        context['theme'] = None
        return context
