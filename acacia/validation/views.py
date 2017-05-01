import os, tempfile, json, re
import time
import pandas as pd
import numpy as np

from django.shortcuts import get_object_or_404, redirect
from django.conf import settings
from django.core.files.storage import default_storage
from django.views.generic import FormView, TemplateView, DetailView
from django.views.decorators.gzip import gzip_page
from django.http.response import HttpResponse
from django.core.urlresolvers import reverse

from acacia.validation.models import Validation, Result, ValidPoint
from acacia.data.util import slugify
from acacia.validation.forms import UploadFileForm, ValidationForm
from acacia.data.views import SeriesView, date_handler

import logging
from datetime import datetime
logger = logging.getLogger(__name__)

def accept(request, pk):
    ''' accept all and remove invalid points from validation '''
    val = get_object_or_404(Validation,pk=pk)   
    pts = val.validpoint_set
    if pts:
        begin = pts.first().date
        end = pts.last().date
        val.validpoint_set.filter(value__isnull=True).delete()
        defaults={'begin':begin,'end':end,'user':request.user,'xlfile':None,'valid':True, 'date': datetime.now(), 'remarks': 'Alles geaccepteerd'}
    
        result,created = Result.objects.get_or_create(validation=val,defaults=defaults)
        if not created:
            result.__dict__.update(defaults)
            result.save()

    return redirect(val.get_absolute_url())
    
def update_stats(request, pk):
    ''' update statistics of series on a validation page '''
    val = get_object_or_404(Validation,pk=pk)
    val.series.getproperties().update()
    return redirect(val.get_absolute_url())
    
def remove_result(request, pk):
    ''' removes validation result '''
    result = get_object_or_404(Result,pk=pk)
    val = result.validation
    result.delete()
    val.validpoint_set.all().delete()
    val.persist()
    return redirect(val.get_absolute_url())

def remove_points(request, pk):
    ''' removes validated points and subresults'''
    val = get_object_or_404(Validation,pk=pk)
    val.subresult_set.all().delete()
    val.validpoint_set.all().delete()
    return redirect(val.get_absolute_url())
    
def validate(request, pk):
    ''' validates timeseries '''
    val = get_object_or_404(Validation,pk=pk)
    val.persist()
    return redirect(val.get_absolute_url())

def download(request, pk):
    ''' download Excel file for validation '''
    validation = get_object_or_404(Validation,pk=pk)
    
    pts = [(p.date,p.value) for p in validation.series.datapoints.all()]
    index,data = zip(*pts)
    raw = pd.Series(data,index)

    pts = [(p.date,p.value) for p in validation.validpoint_set.all()]
    index,data = zip(*pts)
    val = pd.Series(data,index)
        
    val = val.groupby(level=0).last()
    raw = raw.groupby(level=0).last()

    # build dataframe with both raw and validated time series
    df = pd.DataFrame({'raw (id=%d)' % validation.series.id: raw, 'validated (id=%d)' % validation.id: val})

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

class ValidationError(Exception):
    pass

def process_file(request, path):
    # read excel file as pandas dataframe
    logger.debug('Processing validation file '+path)
    df = pd.read_excel(path,index_col=0)
    rows,cols = df.shape
    if cols != 2:
        raise ValidationError('Validation file must have three columns')
    logger.debug('{} rows read'.format(rows))

    # get id of validation instance
    raw, val = df.columns
    m = re.search(r'id=(\d+)', val)
    if m:
        # get validation instance
        val_id = int(m.group(1))
        val = Validation.objects.get(pk=val_id)
    else:
        raise ValidationError('Format error in header')
    # drop N/A values
    df.dropna(how='all',inplace=True)
    df.sort_index(inplace=True)
    relpath = os.path.join(settings.MEDIA_URL,os.path.relpath(path,default_storage.location))
    begin = df.index[0]
    end = df.index[-1]
    defaults={'begin':begin,'end':end,'user':request.user,'xlfile':relpath,'valid':True, 'date': datetime.now()}

    #result,updated = Result.objects.update_or_create(validation=val,defaults=defaults)
    
    result,created = Result.objects.get_or_create(validation=val,defaults=defaults)
    if not created:
        result.__dict__.update(defaults)
        result.save()
    
    # update valid points
    pts = [ValidPoint(validation=val,date=date,value=None if np.isnan(values[1]) else values[1]) for date,values in df.iterrows()]
    #val.validpoint_set.filter(date__range=[begin,end]).delete()
    val.validpoint_set.all().delete()
    val.validpoint_set.bulk_create(pts)

    # revalidate
    val.persist()
    
def process_uploaded_files(request, files):
    logger.debug('Processing {} uploaded validation files'.format(len(files)))
    for f in files:
        process_file(request,f)
        
class UploadFileView(FormView):

    template_name = 'upload.html'
    form_class = UploadFileForm
    success_url = 'up/1/done'
    
    def get_success_url(self):
#        return self.success_url
#         url = reverse('validation:validation-detal',kwargs=self.kwargs)
#         return url + '?next=' + self.request.get_full_path()
        return reverse('validation:validation-detail', kwargs=self.kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(UploadFileView, self).get_context_data(**kwargs)
        context['validation'] = get_object_or_404(Validation,pk=int(self.kwargs.get('pk')))
        return context

    def form_valid(self, form):

        # download files to upload folder
        local_files = []
        for f in form.files.getlist('filename'):
            path = save_file(f,'valid')
            local_files.append(path)

        process_uploaded_files(self.request, local_files)
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
    ''' return three series: raw, validated and invalid '''
    validation = get_object_or_404(Validation,pk=pk)
    options = {'start': request.GET.get('start', None),
               'stop': request.GET.get('stop', None)}

    raw_options = options
    raw_options['raw'] = True
    raw = validation.series.to_pandas(**raw_options)
    val = validation.to_pandas(**options)
    
    if val.size == 0:
        val = pd.Series(data=np.nan,index=raw.index)
        hasval = False
    else:
        hasval = True

    inv = validation.invalid_points
    if inv:
        index, data = zip(*[(p.date, 1.0) for p in inv])
        inv = pd.Series(data,index)
        hasinv = True
    else:
        inv = pd.Series(data=np.nan,index=raw.index)
        hasinv = False
    
    raw = raw.groupby(level=0).last()
    val = val.groupby(level=0).last()
    inv = inv.groupby(level=0).last()
    df = pd.DataFrame({'raw':raw,'valid': val, 'invalid': inv})
    if not hasval:
        df['valid'] = np.nan
    if not hasinv:
        df['invalid'] = np.nan
    else:
        df['invalid'] = df['invalid'] * df['raw']

    #df.dropna(how='all',inplace=True)
    df.sort_index(inplace=True)

    def nn(x):
        # replace NaN with None for json converter
        return None if pd.isnull(x) else x
    
    pts = [(index,nn(row['raw']),nn(row['valid']),nn(row['invalid'])) for index,row in df.iterrows()]
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
           
        series = [{'name': 'raw', 'type': ser.type, 'data': [], 'color': 'gray' },
                {'name': 'valid', 'type': ser.type, 'data': [], 'color': 'green' }, 
                {'name': 'invalid', 'type': 'scatter', 'data': [], 'color': 'red', 'marker': {'symbol': 'circle'} } 
                ]                 

        options['series'] = series
        jop = json.dumps(options,default=date_handler)
        # remove quotes around date stuff
        jop = re.sub(r'\"(Date\.UTC\([\d,]+\))\"',r'\1', jop)

        context['options'] = jop
        context['theme'] = None
        return context
