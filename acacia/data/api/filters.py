import rest_framework_filters as filters 
from acacia.data.models import SourceFile, Datasource

class DatasourceFilter(filters.FilterSet):
    class Meta:
        model = Datasource
        fields = {
            'name':'__all__'
        }
    
class SourceFileFilter(filters.FilterSet):
    datasource = filters.RelatedFilter(DatasourceFilter,queryset=Datasource.objects.all())
    class Meta:
        model = SourceFile
        fields = {
            'datasource':'__all__',
            'start': '__all__',
            'stop': '__all__'
        }
