'''
Created on Jul 8, 2014

@author: theo
'''
import os
from django.utils.text import slugify
from .util import make_chart
 
def make_wellcharts(modeladmin, request, queryset):
    for w in queryset:
        if not w.has_data():
            continue
        if w.chart.name is None:
            w.chart.name = os.path.join(w.chart.field.upload_to, slugify(unicode(w.name)) +'.png')
            w.save()
            imagedir = os.path.dirname(w.chart.path)
            if not os.path.exists(imagedir):
                os.makedirs(imagedir)
        with open(w.chart.path,'wb') as f:
            f.write(make_chart(w))
        
make_wellcharts.short_description = "Grafieken vernieuwen van geseleceerde putten"
    
    
def make_screencharts(modeladmin, request, queryset):
    for s in queryset:
        if not s.has_data():
            continue
        if s.chart.name is None:
            s.chart.name = os.path.join(s.chart.field.upload_to, slugify(unicode(s)) +'.png')
            s.save()
            imagedir = os.path.dirname(s.chart.path)
            if not os.path.exists(imagedir):
                os.makedirs(imagedir)
        with open(s.chart.path,'wb') as f:
            f.write(make_chart(s))
        
make_screencharts.short_description = "Grafieken vernieuwen van geseleceerde filters"
    