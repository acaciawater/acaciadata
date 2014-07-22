'''
Created on Jul 17, 2014

@author: theo
'''
from django.conf.urls import patterns, url
from .views import VICDetailView, VICGroupView

urlpatterns = patterns('vic.views',
    url(r'^$', VICDetailView.as_view(), name='vic-home'),
    url(r'^(?P<name>\w+)$', VICGroupView.as_view(), name='vic-dashboard'),
    #url(r'^(?P<name>\w+)$', DashView.as_view()),
)
