from django.conf.urls import url
from acacia.meetnet.sensor.views import LoggerAddView, LoggerAddedView,\
    LoggerMoveView, LoggerMovedView, LoggerStartedView, LoggerStartView,\
    LoggerStopView, LoggerStoppedView, LoggerRefreshedView, LoggerRefreshView

urlpatterns = [
    url(r'add/(?P<pk>\d+)/done$', LoggerAddedView.as_view(), name='add-done'),
    url(r'add', LoggerAddView.as_view(), name='add'),
    url(r'move/(?P<pk>\d+)/done$', LoggerMovedView.as_view(), name='move-done'),
    url(r'move', LoggerMoveView.as_view(), name='move'),
    url(r'start/(?P<pk>\d+)/done$', LoggerStartedView.as_view(), name='start-done'),
    url(r'start', LoggerStartView.as_view(), name='start'),
    url(r'stop/(?P<pk>\d+)/done$', LoggerStoppedView.as_view(), name='stop-done'),
    url(r'stop', LoggerStopView.as_view(), name='stop'),
    url(r'refresh/(?P<pk>\d+)/done$', LoggerRefreshedView.as_view(), name='refresh-done'),
    url(r'refresh', LoggerRefreshView.as_view(), name='refresh'),
]