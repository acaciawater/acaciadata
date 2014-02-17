from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from data.views import DataFileAddView, DataFileDetailView, ChartView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'acacia.views.home', name='home'),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^knmi/', include('acacia.data.knmi.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^data/', include('acacia.data.urls')),
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
