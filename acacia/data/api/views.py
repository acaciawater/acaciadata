from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from acacia.data.models import MeetLocatie, Datasource, Parameter, DataPoint, \
    Series, SourceFile

from .filters import SourceFileFilter, TimeseriesFilter, DatasourceFilter
from .serializers import TimeseriesSerializer, \
    MeetLocatieSerializer, DatasourceSerializer, ParameterSerializer, \
    DataPointSerializer, SourceFileSerializer


class MeetLocatieViewSet(ModelViewSet):
    serializer_class = MeetLocatieSerializer
    queryset = MeetLocatie.objects.all()

class DatasourceViewSet(ModelViewSet):
    serializer_class = DatasourceSerializer
    queryset = Datasource.objects.all()
    filter_class = DatasourceFilter

class SourceFileViewSet(ModelViewSet):
    serializer_class = SourceFileSerializer
    queryset = SourceFile.objects.all()
    filter_class = SourceFileFilter
    
class ParameterViewSet(ModelViewSet):
    serializer_class = ParameterSerializer
    queryset = Parameter.objects.all()
    
class DataPointViewSet(ModelViewSet):
    ''' returns a list of (raw) datapoints '''
    serializer_class = DataPointSerializer
    queryset = DataPoint.objects.all()
    filter_fields = ('series',)
    
class TimeseriesViewSet(ModelViewSet):
    serializer_class = TimeseriesSerializer
    queryset = Series.objects.all()
    filter_class = TimeseriesFilter
    
    @action(detail=True)
    def data(self, request, pk):
        ''' returns data of a time series '''
        queryset = self.get_queryset()
        series = get_object_or_404(queryset, pk=pk)
        params = request.query_params
        data = series.to_array(**params)
        return Response(data)
