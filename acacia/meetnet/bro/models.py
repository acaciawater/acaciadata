# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your models here.

# This is an auto-generated Django model module created by ogrinspect.
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point

class MapSheet(models.Model):
    area = models.FloatField()
    perimeter = models.FloatField()
    topo_2561_field = models.IntegerField()
    topo_25611 = models.IntegerField()
    bladnaam = models.CharField(max_length=20)
    nr = models.IntegerField()
    ltr = models.CharField(max_length=1)
    district = models.CharField(max_length=2)
    blad = models.CharField(max_length=3)
    geom = models.PolygonField(srid=28992)
    
    @classmethod
    def from_location(cls, location, srid=28992):
        ''' return mapsheet queryset for a location. 
        Location can be a geos.Point or (x,y) tuple. 
        When tuple is given, the srid is required '''
        if type(location) in [list,tuple]:
            point=Point(location,srid=srid)
        else:
            point=location
        point.transform(28992)
        return cls.objects.filter(geom__contains=point)
        