from django.conf.urls import patterns, url
from django.views.generic import DetailView
from django.views.generic.list import ListView
from .models import Project, ProjectLocatie, MeetLocatie
from .views import DataFileAddView, DataFileDetailView, ChartView, ChartBareView, DashView, SeriesView


urlpatterns = patterns('acacia.data.views',
    url(r'^$', ListView.as_view(model=Project), name='project-list'),
    url(r'^file/(?P<pk>\d+)/$', DataFileDetailView.as_view(), name='datafile-detail'),
    url(r'^series/(?P<pk>\d+)/$', SeriesView.as_view(), name='series-detail'),
    url(r'^add/$', DataFileAddView.as_view(), name='datafile-add'),
    url(r'^chart/(?P<pk>\d+)/$', ChartBareView.as_view(), name='bare-chart'),
    url(r'^view/(?P<slug>\w+)/$', ChartView.as_view(), name='chart-view'),
    url(r'^dash/(?P<slug>\w+)/$', DashView.as_view(), name='dash-view'),

    url(r'^(?P<slug>\w+)/$', DetailView.as_view(model=Project), name='project-detail'),
    url(r'^(\w+)/(?P<slug>\w+)$', DetailView.as_view(model=ProjectLocatie), name='projectlocatie-detail'),
    url(r'^(\w+)/(\w+)/(?P<slug>\w+)$', DetailView.as_view(model=MeetLocatie), name='meetlocatie-detail'),
)
