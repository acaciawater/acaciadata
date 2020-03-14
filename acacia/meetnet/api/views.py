from rest_framework.viewsets import ModelViewSet
from acacia.meetnet.api.serializers import WellSerializer, ScreenSerializer,\
    HandpeilingSerializer, InstallationSerializer, LoggerSerializer
from acacia.meetnet.models import Well, Screen, Handpeilingen, LoggerPos,\
    Datalogger
    
class WellViewSet(ModelViewSet):
    serializer_class = WellSerializer
    queryset = Well.objects.all()
    
class ScreenViewSet(ModelViewSet):
    serializer_class = ScreenSerializer
    queryset = Screen.objects.all()

class HandpeilingViewSet(ModelViewSet):
    serializer_class = HandpeilingSerializer
    queryset = Handpeilingen.objects.all()

class InstallationViewSet(ModelViewSet):
    serializer_class = InstallationSerializer
    queryset = LoggerPos.objects.order_by('start_date')
    filter_fields = ('logger','screen',)

class LoggerViewSet(ModelViewSet):
    serializer_class = LoggerSerializer
    queryset = Datalogger.objects.all()
