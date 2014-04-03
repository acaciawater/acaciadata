from django.conf.urls import patterns, url
from .views import SpaarwaterDetailView, BreezandView

urlpatterns = patterns('spaarwater.views',
    url(r'^$', SpaarwaterDetailView.as_view(), name='spaarwater-home'),
    url(r'^[Bb]reezand$', BreezandView.as_view(), name='breezand'),
)
