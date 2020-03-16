import rest_framework_filters as filters 
from acacia.meetnet.models import LoggerPos, Datalogger, Screen, Well, Photo
from acacia.data.api.filters import DatasourceFilter
from acacia.data.models import Datasource, SourceFile

class WellFilter(filters.FilterSet):
    class Meta:
        model = Well
        fields = {
            'name': '__all__',
            'nitg': '__all__',
        }

class ScreenFilter(filters.FilterSet):
    well = filters.RelatedFilter(WellFilter, queryset=Well.objects.all())
    class Meta:
        model = Screen
        fields = {
            'nr': '__all__',
        }
        
class PhotoFilter(filters.FilterSet):
    well = filters.RelatedFilter(WellFilter, queryset=Well.objects.all())
    class Meta:
        model = Photo
        fields = {'well': '__all__'}
    
class LoggerFilter(filters.FilterSet):
    class Meta:
        model = Datalogger
        fields = {
            'serial':'__all__',
            'model':'__all__',
        }

class InstallationFilter(filters.FilterSet):
    screen = filters.RelatedFilter(ScreenFilter, queryset=Screen.objects.all())
    logger = filters.RelatedFilter(LoggerFilter, queryset=Datalogger.objects.all())

    class Meta:
        model = LoggerPos
        fields = {
            'start_date':'__all__',
            'end_date':'__all__',
        }
    
class SourceFileFilter(filters.FilterSet):
    ''' special filter to allow queries to retrieve all source files for a well.
    Example: http://localhost:8000/api/v1/files/?install__screen__well__name=MW-PB17
    '''
    datasource = filters.RelatedFilter(DatasourceFilter,queryset=Datasource.objects.all())
    install = filters.RelatedFilter(InstallationFilter, name='loggerpos', queryset=LoggerPos.objects.all())
    
    class Meta:
        model = SourceFile
        fields = {
            'name': '__all__',
            'start': '__all__',
            'stop': '__all__'
        }
