'''
Created on Nov 1, 2019

@author: theo
'''
from django.conf.urls import url
from acacia.meetnet.bro.views import download_gmw

urlpatterns = [
    url(r'^gmw/',download_gmw,name='gmw'),
]
