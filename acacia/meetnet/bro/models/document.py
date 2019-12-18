from django.db import models
from acacia.meetnet.bro.models import GroundwaterMonitoringWell

class SourceDocument(models.Model):
    pass

class GMW_Construction(SourceDocument):
    gmw = models.ForeignKey(GroundwaterMonitoringWell, on_delete=models.CASCADE)
