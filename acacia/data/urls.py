from django.conf.urls import patterns, url
from django.views.generic.list import ListView
from acacia.data.models import Project
from acacia.data.views import DatasourceDetailView, DatasourceAsZip, DatasourceAsCsv, ProjectDetailView, ProjectLocatieDetailView, \
    MeetLocatieDetailView, MeetlocatieAsZip, SeriesAsCsv, SeriesToJson, ChartToJson, GridToJson, ChartAsCsv, UpdateMeetlocatie, ChartView, \
    ChartBaseView, DashView, TabGroupView, SeriesView, GridBaseView, GridView, UpdateDatasource, StartUpdateDatasource, poll_state

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
    url(r'^update/meetlocatie/(?P<pk>\d+)', UpdateMeetlocatie,name='meetlocatie-update'),
    
    url(r'^start/(?P<pk>\d+)',StartUpdateDatasource,name='start-datasource-update'),
    url(r'^start/poll_state$', poll_state, name="poll_state"),
        
    url(r'^get/series/(?P<pk>\d+)/$', SeriesToJson),
    url(r'^get/chart/(?P<pk>\d+)/$', ChartToJson),
    url(r'^get/grid/(?P<pk>\d+)/$', GridToJson),
    
    url(r'^series/(?P<pk>\d+)/$', SeriesView.as_view(), name='series-detail'),
    url(r'^chart/(?P<pk>\d+)/$', ChartBaseView.as_view(), name='chart-detail'),
    url(r'^grid/(?P<pk>\d+)$', GridBaseView.as_view(), name='grid-detail'),
    url(r'^grafiek/(?P<pk>\d+)/$', ChartView.as_view(), name='chart-view'),
    url(r'^profiel/(?P<pk>\d+)$', GridView.as_view(), name='grid-view'),
    url(r'^dashboard/(?P<pk>\d+)/$', DashView.as_view(), name='dash-view'),
    url(r'^tabs/(?P<pk>\d+)/$', TabGroupView.as_view(), name='tabgroup'),
    url(r'^project/(?P<pk>\d+)/$', ProjectDetailView.as_view(), name='project-detail'),
    url(r'^locatie/(?P<pk>\d+)$', ProjectLocatieDetailView.as_view(), name='projectlocatie-detail'),
    url(r'^meetlocatie/(?P<pk>\d+)$', MeetLocatieDetailView.as_view(), name='meetlocatie-detail'),
    
)
