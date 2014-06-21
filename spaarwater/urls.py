from django.conf.urls import patterns, url
from .views import SpaarwaterDetailView, DashGroupView

urlpatterns = patterns('spaarwater.views',
    url(r'^$', SpaarwaterDetailView.as_view(), name='spaarwater-home'),
    url(r'^(?P<name>\w+)$', DashGroupView.as_view(), name='spaarwater-dashboard'),
    #url(r'^(?P<name>\w+)$', DashView.as_view()),
)
