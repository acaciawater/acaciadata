from django.conf.urls import url
from acacia.meetnet.sensor.views import LoggerAddView, LoggerAddedView,\
    LoggerMoveView, LoggerMovedView, LoggerStartedView, LoggerStartView,\
    LoggerStopView, LoggerStoppedView

urlpatterns = [
    url(r'add/done/(?P<pk>\d+)$', LoggerAddedView.as_view(), name='add-done'),
    url(r'add', LoggerAddView.as_view(), name='add'),
    url(r'move/done/(?P<pk>\d+)$', LoggerMovedView.as_view(), name='move-done'),
    url(r'move', LoggerMoveView.as_view(), name='move'),
    url(r'start/done/(?P<pk>\d+)$', LoggerStartedView.as_view(), name='start-done'),
    url(r'start', LoggerStartView.as_view(), name='start'),
    url(r'stop/done/(?P<pk>\d+)$', LoggerStoppedView.as_view(), name='stop-done'),
    url(r'stop', LoggerStopView.as_view(), name='stop'),
]