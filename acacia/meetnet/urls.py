from django.conf.urls import patterns, url
from .views import NetworkView, WellView, ScreenView, WellChartView

urlpatterns = patterns('acacia.meetnet.views',
    url(r'^$', NetworkView.as_view(), name='home'),
    url(r'^(?P<pk>\d+)$', NetworkView.as_view(), name='network-detail'),
    url(r'^well/(?P<pk>\d+)$', WellView.as_view(), name='well-detail'),
    url(r'^screen/(?P<pk>\d+)$', ScreenView.as_view(), name='screen-detail'),
    url(r'^chart/(?P<pk>\d+)/$', WellChartView.as_view(), name='chart-detail'),
    url(r'^info/(?P<pk>\d+)/$', 'wellinfo', name='well-info'),
)
