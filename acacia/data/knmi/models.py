from django.db import models

class Station(models.Model):
    nummer = models.IntegerField()
    naam = models.CharField(max_length=50)
    xcoord = models.FloatField()
    ycoord = models.FloatField()
    lon = models.FloatField()        
    lat = models.FloatField()        
        
    def __unicode__(self):
        return self.naam

class NeerslagStation(models.Model):
    nummer = models.IntegerField()
    naam = models.CharField(max_length=50)
    xcoord = models.FloatField()
    ycoord = models.FloatField()
    lon = models.FloatField()        
    lat = models.FloatField()
            
    def __unicode__(self):
        return self.naam

