from rest_framework.viewsets import ModelViewSet
from acacia.meetnet.api.serializers import WellSerializer, ScreenSerializer,\
    HandpeilingSerializer, InstallationSerializer, LoggerSerializer,\
    PhotoSerializer
from acacia.meetnet.models import Well, Screen, Handpeilingen, LoggerPos,\
    Datalogger, Photo
from acacia.meetnet.api.filters import InstallationFilter, LoggerFilter,\
    SourceFileFilter, ScreenFilter, WellFilter, PhotoFilter
from acacia.data.api.serializers import SourceFileSerializer
from acacia.data.models import SourceFile
    
class WellViewSet(ModelViewSet):
    serializer_class = WellSerializer
    queryset = Well.objects.all()
    filter_class = WellFilter

class PhotoViewSet(ModelViewSet):
    serializer_class = PhotoSerializer
    queryset = Photo.objects.all()
    filter_class = PhotoFilter
  
class ScreenViewSet(ModelViewSet):
    serializer_class = ScreenSerializer
    queryset = Screen.objects.all()
    filter_class = ScreenFilter

class HandpeilingViewSet(ModelViewSet):
    serializer_class = HandpeilingSerializer
    queryset = Handpeilingen.objects.all()

class InstallationViewSet(ModelViewSet):
    serializer_class = InstallationSerializer
    queryset = LoggerPos.objects.order_by('start_date')
    filter_class = InstallationFilter

class LoggerViewSet(ModelViewSet):
    serializer_class = LoggerSerializer
    queryset = Datalogger.objects.all()
    filter_class = LoggerFilter

class SourceFileViewSet(ModelViewSet):
    serializer_class = SourceFileSerializer
    queryset = SourceFile.objects.all()
    filter_class = SourceFileFilter
