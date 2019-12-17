'''
Created on Nov 1, 2019

@author: theo
'''
from django.conf.urls import url
from acacia.meetnet.bro.views import download_gmw, DefaultsView

urlpatterns = [
    url(r'^gmw/',download_gmw,name='gmw'),
    url(r'^defaults/(?P<pk>\d+)/$',DefaultsView.as_view(),name='defaults'),
]
