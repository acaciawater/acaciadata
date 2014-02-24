from models import Station, NeerslagStation
from django.contrib.gis import admin

admin.site.register(Station,admin.OSMGeoAdmin)
admin.site.register(NeerslagStation,admin.OSMGeoAdmin)
