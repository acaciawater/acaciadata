'''
Created on Feb 19, 2016

@author: theo
'''
from django.conf.urls import url
from acacia.data.events.views import testevent

urlpatterns = [
    url(r'^(?P<pk>\d+)', testevent),
]
