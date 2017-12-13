from models import Station, NeerslagStation
from django.contrib.gis import admin
from acacia.data.knmi.util import create_location
from django.contrib import messages
from acacia.data.models import Project

def create(modeladmin, request, queryset):
    ncreated = 0
    nfail = 0
    nupdated = 0
    project = Project.objects.first()
    for station in queryset:
        try:
            created = create_location(station,project)
            if created:
                ncreated += 1
            else:
                nupdated += 1
        except:
            nfail += 1
    if ncreated:
        messages.success(request, '{} locations successfully created, {} updated.'.format(ncreated,nupdated))
    elif nupdated:
        messages.info(request, '{} locations successfully updated.'.format(nupdated))
    if nfail:
        messages.error(request, 'Failed to create or update {} locations.'.format(nfail))
        
create.short_description = 'Locaties aanmaken'

class StationAdmin(admin.OSMGeoAdmin):
    model = Station
    search_fields = ['naam',]
    list_display = ('naam', 'nummer','coords')
    actions = [create,]
admin.site.register(Station,StationAdmin)
admin.site.register(NeerslagStation,StationAdmin)
