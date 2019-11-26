from django.conf.urls import url
from views import download, UploadFileView, update_stats, accept, validate, remove_file
from django.contrib import admin
from acacia.validation.views import SeriesView, ValToJson, ValidationView, reset

urlpatterns = [url(r'down/(?P<pk>\d+)$', download, name='download'),
               url(r'up/(?P<pk>\d+)$', UploadFileView.as_view(), name='upload'),
#               url(r'up/(?P<pk>\d+)/done$', UploadDoneView.as_view(), name='upload_done'),
               url(r'show/(?P<pk>\d+)$', SeriesView.as_view(), name='show'),
               url(r'get/(?P<pk>\d+)$', ValToJson),
               url(r'del/(?P<pk>\d+)$', reset, name='reset'),
               url(r'accept/(?P<pk>\d+)$', accept, name='accept'),
               url(r'validate/(?P<pk>\d+)$', validate, name='validate'),
               url(r'rm/(?P<pk>\d+)$', remove_file, name='remove_file'),
               url(r'stats/(?P<pk>\d+)$', update_stats, name='stats'),
               url(r'val/(?P<pk>\d+)$', ValidationView.as_view(),name='validation-detail'),
#               url(r'val/(?P<pk>\d+/done)$', UploadDoneView.as_view(),name='validation_done'),
]
