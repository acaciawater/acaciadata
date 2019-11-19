from django.conf.urls import url
from .views import NetworkView, WellView, ScreenView, WellChartView, EmailNetworkSeries, EmailNetworkNITG, EmailScreenSeries, EmailWellSeries, UploadDoneView, UploadFileView
from acacia.meetnet.views import wellinfo, json_series, DownloadWellSeries,\
    change_refpnt, AddLoggerView, LoggerAddedView, UploadRegistrationView

urlpatterns = [
    url(r'^$', NetworkView.as_view(), name='home'),
    url(r'^(?P<pk>\d+)$', NetworkView.as_view(), name='network-detail'),
    url(r'^well/(?P<pk>\d+)$', WellView.as_view(), name='well-detail'),
    url(r'^screen/(?P<pk>\d+)$', ScreenView.as_view(), name='screen-detail'),
    url(r'^chart/(?P<pk>\d+)/$', WellChartView.as_view(), name='chart-detail'),
    url(r'^info/(?P<pk>\d+)/$', wellinfo, name='well-info'),
    url(r'^added/(?P<pk>\d+)$', LoggerAddedView.as_view(), name='logger-added'),
    url(r'^add', AddLoggerView.as_view(), name='add-logger'),
    # TODO redesign urls for download
    url(r'^data/(?P<pk>\d+)/$', json_series, name='screen-series'),
    url(r'^data/well/(?P<pk>\d+)/$', DownloadWellSeries, name='download-well'),
    url(r'^email/network/(?P<pk>\d+)', EmailNetworkSeries,name='email-network'),
    url(r'^email/nitg/(?P<pk>\d+)', EmailNetworkNITG,name='email-network-nitg'),
    url(r'^email/well/(?P<pk>\d+)', EmailWellSeries,name='email-well'),
    url(r'^email/screen/(?P<pk>\d+)', EmailScreenSeries,name='email-screen'),
    url(r'^upload/(?P<id>\d+)/$', UploadFileView.as_view(), name='upload_files'),
    url(r'^done/(?P<id>\d+)/$', UploadDoneView.as_view(), name='upload_done'),
    url(r'^ref/(?P<pk>\d+)/$', change_refpnt, name='change_ref'),
    url(r'^reg/$', UploadRegistrationView.as_view(), name='upload_registration'),
    
    ]
