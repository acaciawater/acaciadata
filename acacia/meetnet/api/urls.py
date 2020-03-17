from django.conf.urls import url, include
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import APIRootView, DefaultRouter
from rest_framework.schemas import get_schema_view

from acacia.data.api.views import TimeseriesViewSet, MeetLocatieViewSet, \
    DatasourceViewSet, DataPointViewSet
from acacia.meetnet.api.views import WellViewSet, ScreenViewSet, LoggerViewSet,\
    InstallationViewSet, SourceFileViewSet, PhotoViewSet, HandpeilingViewSet


class MeetnetApiView(APIRootView):
    ''' REST API for Monitoring networks '''
    pass

class MeetnetRouter(DefaultRouter):
    APIRootView = MeetnetApiView
    

router = MeetnetRouter()
router.register('wells', WellViewSet)
router.register('screens', ScreenViewSet)
router.register('photos', PhotoViewSet)
router.register('loggers', LoggerViewSet)
router.register('installations', InstallationViewSet)
router.register('manual', HandpeilingViewSet)

router.register('locations', MeetLocatieViewSet)
router.register('sources', DatasourceViewSet)
router.register('files', SourceFileViewSet)
router.register('series', TimeseriesViewSet)
router.register('data', DataPointViewSet)

schema_view = get_schema_view(title='Meetnet API')

urlpatterns = [
    url('schema/', schema_view),
    url('docs/', include_docs_urls(title='Meetnet API')),
    url('', include(router.urls)),
]
