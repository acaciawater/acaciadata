from django.contrib.gis.db import models
from acacia.data import util

class Station(models.Model):
    nummer = models.IntegerField()
    naam = models.CharField(max_length=50)
    location = models.PointField(srid=util.RDNEW)
    objects = models.GeoManager()
        
    def __unicode__(self):
        return self.naam

class NeerslagStation(models.Model):
    nummer = models.IntegerField()
    naam = models.CharField(max_length=50)
    location = models.PointField(srid=util.RDNEW)
    objects = models.GeoManager()
            
    def __unicode__(self):
        return self.naam
