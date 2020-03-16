from rest_framework import serializers
from acacia.data.models import DataPoint, Series, MeetLocatie, Datasource,\
    Parameter, SourceFile

class MeetLocatieSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetLocatie
        fields = ['id','name','description','location']
        
class DatasourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Datasource
        fields = ['id','name','description','meetlocatie','generator','timezone','config','url','username']

class SourceFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceFile
        fields = ['id','name','datasource','file','crc']
        
class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ['id','name','description','datasource','unit','type']
                
class DataPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataPoint
        fields = ['series','date','value']

class MeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataPoint
        fields = ['date','value']

class TimeseriesSerializer(serializers.ModelSerializer):
#     data = MeasurementSerializer(many=True,read_only=True,source='datapoints')
    class Meta:
        model = Series
        fields = ['id','name','description','unit','type','timezone']
        