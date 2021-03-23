from django.shortcuts import get_object_or_404
from rest_framework.decorators import action, detail_route
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from acacia.data.api.serializers import SourceFileSerializer
from acacia.data.models import SourceFile
from acacia.meetnet.models import Well, Screen, Handpeilingen, LoggerPos, \
    Datalogger, Photo

from .filters import InstallationFilter, LoggerFilter, \
    SourceFileFilter, ScreenFilter, WellFilter, PhotoFilter
from .serializers import WellSerializer, ScreenSerializer, \
    HandpeilingSerializer, InstallationSerializer, LoggerSerializer, \
    PhotoSerializer


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

    @action(detail=True)
    def data(self, request, pk):
        ''' returns data '''
        queryset = self.get_queryset()
        series = get_object_or_404(queryset, pk=pk)
        data = series.to_array()
        return Response(data)

class InstallationViewSet(ModelViewSet):
    serializer_class = InstallationSerializer
    queryset = LoggerPos.objects.order_by('start_date')
    filter_class = InstallationFilter

class LoggerViewSet(ModelViewSet):
    serializer_class = LoggerSerializer
    queryset = Datalogger.objects.all()
    filter_class = LoggerFilter

    @action(detail=True)
    def current(self, request, pk):
        ''' return current installation '''
        queryset = self.get_queryset()
        logger = get_object_or_404(queryset, pk=pk)
        install = logger.loggerpos_set.latest('start_date')
        serializer = InstallationSerializer(install)
        return Response(serializer.to_representation(install))
        
class SourceFileViewSet(ModelViewSet):
    serializer_class = SourceFileSerializer
    queryset = SourceFile.objects.all()
    filter_class = SourceFileFilter
