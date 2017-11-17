from django.conf.urls import url
from .views import NetworkView, WellView, ScreenView, WellChartView, EmailNetworkSeries, EmailNetworkNITG, EmailScreenSeries, EmailWellSeries, UploadDoneView, UploadFileView
from django.contrib.auth.decorators import login_required
from acacia.meetnet.views import wellinfo, json_series, DownloadWellSeries

urlpatterns = [
    url(r'^$', NetworkView.as_view(), name='home'),
    url(r'^(?P<pk>\d+)$', NetworkView.as_view(), name='network-detail'),
    url(r'^well/(?P<pk>\d+)$', WellView.as_view(), name='well-detail'),
    url(r'^screen/(?P<pk>\d+)$', ScreenView.as_view(), name='screen-detail'),
    url(r'^chart/(?P<pk>\d+)/$', WellChartView.as_view(), name='chart-detail'),
    url(r'^info/(?P<pk>\d+)/$', wellinfo, name='well-info'),
    # TODO redesign urls for download
    url(r'^data/(?P<pk>\d+)/$', json_series, name='screen-series'),
    url(r'^data/well/(?P<pk>\d+)/$', DownloadWellSeries, name='download-well'),
    url(r'^email/network/(?P<pk>\d+)', EmailNetworkSeries,name='email-network'),
    url(r'^email/nitg/(?P<pk>\d+)', EmailNetworkNITG,name='email-network-nitg'),
    url(r'^email/well/(?P<pk>\d+)', EmailWellSeries,name='email-well'),
    url(r'^email/screen/(?P<pk>\d+)', EmailScreenSeries,name='email-screen'),
    url(r'^upload/(?P<id>\d+)/$', login_required(UploadFileView.as_view()), name='upload_files'),
    url(r'^done/(?P<id>\d+)/$', login_required(UploadDoneView.as_view()), name='upload_done')
    ]
