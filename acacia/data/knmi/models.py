from django.contrib.gis.db import models
from ..util import RDNEW

class Station(models.Model):
    nummer = models.IntegerField()
    naam = models.CharField(max_length=50)
    location = models.PointField(srid=RDNEW)
    objects = models.GeoManager()
        
    def __unicode__(self):
        return self.naam

class NeerslagStation(models.Model):
    nummer = models.IntegerField()
    naam = models.CharField(max_length=50)
    location = models.PointField(srid=RDNEW)
    objects = models.GeoManager()
            
    def __unicode__(self):
        return self.naam
