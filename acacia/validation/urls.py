from django.conf.urls import url
from views import download, UploadFileView, UploadDoneView
from django.contrib import admin
from acacia.validation.views import SeriesView, ValToJson, ValidationView

admin.autodiscover()

urlpatterns = [url(r'down/(?P<pk>\d+)$', download, name='download'),
               url(r'up/(?P<pk>\d+)$', UploadFileView.as_view(), name='upload'),
               url(r'up/(?P<pk>\d+)/done$', UploadDoneView.as_view(), name='upload_done'),
               url(r'show/(?P<pk>\d+)$', SeriesView.as_view(), name='show'),
               url(r'get/(?P<pk>\d+)$', ValToJson),
               url(r'val/(?P<pk>\d+)$', ValidationView.as_view()),
               url(r'val/(?P<pk>\d+/done)$', UploadDoneView.as_view(),name='validation_done'),
]
