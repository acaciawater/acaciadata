from django.conf.urls import url
from views import download, UploadFileView, UploadDoneView, remove_result, remove_points, update_stats, accept, validate
from django.contrib import admin
from acacia.validation.views import SeriesView, ValToJson, ValidationView

admin.autodiscover()

urlpatterns = [url(r'down/(?P<pk>\d+)$', download, name='download'),
               url(r'up/(?P<pk>\d+)$', UploadFileView.as_view(), name='upload'),
#               url(r'up/(?P<pk>\d+)/done$', UploadDoneView.as_view(), name='upload_done'),
               url(r'show/(?P<pk>\d+)$', SeriesView.as_view(), name='show'),
               url(r'get/(?P<pk>\d+)$', ValToJson),
               url(r'del/(?P<pk>\d+)$', remove_points, name='remove_points'),
               url(r'accept/(?P<pk>\d+)$', accept, name='accept'),
               url(r'validate/(?P<pk>\d+)$', validate, name='validate'),
               url(r'remove/(?P<pk>\d+)$', remove_result, name='remove_result'),
               url(r'stats/(?P<pk>\d+)$', update_stats, name='stats'),
               url(r'val/(?P<pk>\d+)$', ValidationView.as_view(),name='validation-detail'),
#               url(r'val/(?P<pk>\d+/done)$', UploadDoneView.as_view(),name='validation_done'),
]
