from django.conf.urls import patterns, url
from django.views.generic import DetailView
from django.views.generic.list import ListView
from .models import Project, ProjectLocatie, MeetLocatie
from .views import DatasourceDetailView, DatasourceAsZip, ProjectDetailView, ProjectLocatieDetailView, \
    MeetLocatieDetailView, MeetlocatieAsZip, UpdateMeetlocatie, ChartView, ChartBareView, DashView, SeriesView


urlpatterns = patterns('acacia.data.views',
    url(r'^$', ListView.as_view(model=Project), name='project-list'),
    url(r'^bron/(?P<pk>\d+)/$', DatasourceDetailView.as_view(), name='datasource-detail'),
    url(r'^download/datasource/(?P<pk>\d+)', DatasourceAsZip,name='datasource-zip'),
    url(r'^download/meetlocatie/(?P<pk>\d+)', MeetlocatieAsZip,name='meetlocatie-zip'),
    url(r'^update/meetlocatie/(?P<pk>\d+)', UpdateMeetlocatie,name='meetlocatie-update'),
    url(r'^reeks/(?P<pk>\d+)/$', SeriesView.as_view(), name='series-detail'),
    url(r'^chart/(?P<pk>\d+)/$', ChartBareView.as_view(), name='chart-detail'),
    url(r'^grafiek/(?P<pk>\d+)/$', ChartView.as_view(), name='chart-view'),
    url(r'^dashboard/(?P<pk>\d+)/$', DashView.as_view(), name='dash-view'),
    url(r'^project/(?P<pk>\d+)/$', ProjectDetailView.as_view(), name='project-detail'),
    url(r'^locatie/(?P<pk>\d+)$', ProjectLocatieDetailView.as_view(), name='projectlocatie-detail'),
    url(r'^meetlocatie/(?P<pk>\d+)$', MeetLocatieDetailView.as_view(), name='meetlocatie-detail'),
)
