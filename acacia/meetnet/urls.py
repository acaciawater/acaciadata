from django.conf.urls import url
from .views import NetworkView, WellView, ScreenView, WellChartView, EmailNetworkSeries, EmailScreenSeries, EmailWellSeries, UploadDoneView, UploadFileView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^$', NetworkView.as_view(), name='home'),
    url(r'^(?P<pk>\d+)$', NetworkView.as_view(), name='network-detail'),
    url(r'^well/(?P<pk>\d+)$', WellView.as_view(), name='well-detail'),
    url(r'^screen/(?P<pk>\d+)$', ScreenView.as_view(), name='screen-detail'),
    url(r'^chart/(?P<pk>\d+)/$', WellChartView.as_view(), name='chart-detail'),
    url(r'^info/(?P<pk>\d+)/$', 'acacia.meetnet.views.wellinfo', name='well-info'),
    url(r'^email/network/(?P<pk>\d+)', EmailNetworkSeries,name='email-network'),
    url(r'^email/well/(?P<pk>\d+)', EmailWellSeries,name='email-well'),
    url(r'^email/screen/(?P<pk>\d+)', EmailScreenSeries,name='email-screen'),
    url(r'^upload/(?P<id>\d+)/$', login_required(UploadFileView.as_view()), name='upload_files'),
    url(r'^done/(?P<id>\d+)/$', login_required(UploadDoneView.as_view()), name='upload_done')
    ]
