from django.conf.urls import patterns, include, url
from django.contrib.gis import admin

from importer import importall

urlpatterns = patterns('acacia.data.knmi.views',
#    url(r'^admin/', include(admin.site.urls)),
    url(r'^find', 'find_stations', name='find_stations'),
    url(r'^select', 'select_station', name='select_station'),
#    url(r'^import/', importall(), name='import'),
)
