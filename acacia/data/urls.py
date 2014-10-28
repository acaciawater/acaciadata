from django.conf.urls import patterns, url
from django.views.generic import DetailView
from django.views.generic.list import ListView
from acacia.data.models import Project, ProjectLocatie, MeetLocatie
from acacia.data.views import DatasourceDetailView, DatasourceAsZip, DatasourceAsCsv, ProjectDetailView, ProjectLocatieDetailView, \
    MeetLocatieDetailView, MeetlocatieAsZip, SeriesAsCsv, SeriesToJson, ChartToJson, ChartAsCsv, UpdateMeetlocatie, ChartView, ChartBaseView, \
    DashView, TabGroupView, SeriesView, UpdateDatasource


urlpatterns = patterns('',
    url(r'^$', ListView.as_view(model=Project), name='project-list'),
    url(r'^/$', ListView.as_view(model=Project), name='project-list'),
    url(r'^bron/(?P<pk>\d+)/$', DatasourceDetailView.as_view(), name='datasource-detail'),

    url(r'^download/datasource/(?P<pk>\d+)', DatasourceAsZip,name='datasource-zip'),
    url(r'^download/tabel/(?P<pk>\d+)', DatasourceAsCsv,name='datasource-csv'),
    url(r'^download/meetlocatie/(?P<pk>\d+)', MeetlocatieAsZip,name='meetlocatie-zip'),
    url(r'^download/reeks/(?P<pk>\d+)', SeriesAsCsv,name='series-csv'),
    url(r'^download/grafiek/(?P<pk>\d+)', ChartAsCsv,name='chart-csv'),
    
    url(r'^update/(?P<pk>\d+)',UpdateDatasource,name='datasource-update'),
    
    url(r'^get/series/(?P<pk>\d+)/$', SeriesToJson),
    url(r'^get/chart/(?P<pk>\d+)/$', ChartToJson),
    
    url(r'^update/meetlocatie/(?P<pk>\d+)', UpdateMeetlocatie,name='meetlocatie-update'),
    url(r'^reeks/(?P<pk>\d+)/$', SeriesView.as_view(), name='series-detail'),
    url(r'^chart/(?P<pk>\d+)/$', ChartBaseView.as_view(), name='chart-detail'),
    url(r'^grafiek/(?P<pk>\d+)/$', ChartView.as_view(), name='chart-view'),
    url(r'^dashboard/(?P<pk>\d+)/$', DashView.as_view(), name='dash-view'),
    url(r'^tabs/(?P<pk>\d+)/$', TabGroupView.as_view(), name='tabgroup'),
    url(r'^project/(?P<pk>\d+)/$', ProjectDetailView.as_view(), name='project-detail'),
    url(r'^locatie/(?P<pk>\d+)$', ProjectLocatieDetailView.as_view(), name='projectlocatie-detail'),
    url(r'^meetlocatie/(?P<pk>\d+)$', MeetLocatieDetailView.as_view(), name='meetlocatie-detail'),
    
)
