from rest_framework import serializers
from acacia.meetnet.models import Well, Screen, Handpeilingen, Datalogger,\
    LoggerPos

class ScreenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screen
        fields = '__all__'

class WellScreenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screen
        exclude = ['id','mloc','manual_levels','logger_levels','well']

class WellSerializer(serializers.ModelSerializer):
    screens = WellScreenSerializer(many=True, read_only=True, source='screen_set')

    class Meta:
        model = Well
        fields = ['name','nitg','location','description','maaiveld','ahn','date','owner','straat','huisnummer','plaats','postcode','log','screens']

        
class HandpeilingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Handpeilingen
        fields = ['screen','refpnt']

class InstallationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoggerPos
        exclude = ('files',)
                
class LoggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Datalogger
        fields = '__all__'
        
