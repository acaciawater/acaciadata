'''
Created on Feb 19, 2016

@author: theo
'''
from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^(?P<pk>\d+)', 'acacia.data.events.views.testevent'),
)
