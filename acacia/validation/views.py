import os, tempfile, json, time, re
import pandas as pd

from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.files.storage import default_storage
from django.views.generic import FormView, TemplateView, DetailView
from django.views.decorators.gzip import gzip_page
from django.http.response import HttpResponse
from django.core.urlresolvers import reverse

from acacia.validation.models import Validation
from acacia.data.util import slugify
from acacia.validation.forms import UploadFileForm
from acacia.data.views import SeriesView, date_handler

def download(request, pk):
    ''' download Excel file for validation '''
    validation = get_object_or_404(Validation,pk=pk)
    
    pts = [(p.date,p.value) for p in validation.series.datapoints.all()]
    index,data = zip(*pts)
    raw = pd.Series(data=data,index=index)

    pts = [(p.point.date,p.value) for p in validation.validpoint_set.prefetch_related('point')]
    index,data = zip(*pts)
    val = pd.Series(data=data,index=index)
    
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
        return context

def save_file(file_obj,folder):
    path = default_storage.path(os.path.join(folder,file_obj.name))
    with open(path, 'wb') as destination:
        for chunk in file_obj.chunks():
            destination.write(chunk)
    return path

class UploadFileView(FormView):

    template_name = 'upload.html'
    form_class = UploadFileForm
    success_url = 'up/1/done'
    
    def get_success_url(self):
        return reverse('validation:upload_done',kwargs=self.kwargs)

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

@gzip_page
def ValToJson(request, pk):
    ''' return two series: raw and validated '''
    validation = get_object_or_404(Validation,pk=pk)
    pts = [(p.point.date,p.point.value,p.value) for p in validation.validpoint_set.prefetch_related('point')]
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
            'chart': {'type': ser.type, 
                      'animation': False, 
                      'zoomType': 'x',
                      'events': {'load': None},
                      },
            'title': {'text': ser.name},
            'xAxis': {'type': 'datetime'},
            'yAxis': [{'title': {'text': title}}],
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
           
        series = [{'name': ser.name + '(raw)', 'type': ser.type, 'data': [] },
                {'name': ser.name + '(validated)', 'type': ser.type, 'data': [] } ]                 

        options['series'] = series
        jop = json.dumps(options,default=date_handler)
        # remove quotes around date stuff
        jop = re.sub(r'\"(Date\.UTC\([\d,]+\))\"',r'\1', jop)

        context['options'] = jop
        context['theme'] = ' None' #ser.theme()
        return context
