from django.conf.urls import patterns, include, url
from django.contrib.gis import admin

from importer import importall

urlpatterns = patterns('',
#    url(r'^admin/', include(admin.site.urls)),
#    url(r'^import/', importall(), name='import'),
)

#from importer import importall
#urlpatterns = patterns('',
#    url(r'^import/', importall(), name='import'),
#)
