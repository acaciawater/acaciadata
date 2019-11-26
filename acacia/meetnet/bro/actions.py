'''
Created on Nov 19, 2019

@author: theo
'''
from .models import GroundwaterMonitoringWell, MonitoringTube
from django.contrib import messages

def add_bro_for_wells(modeladmin, request, queryset):
    creates = 0
    failures = 0
    updates = 0
    for well in queryset:
        try:
            query = GroundwaterMonitoringWell.objects.filter(well=well)
            if query.exists():
                query.first().update()
                updates += 1
            else:
                GroundwaterMonitoringWell.create_for_well(well)
                creates += 1
        except:
            failures += 1
    if creates:
        messages.success(request,_('BRO information created for %d wells' %creates)) 
    if updates:
        messages.success(request,_('BRO information updated for %d wells' %updates)) 
    if failures:
        messages.error(request,_('Could not create or update BRO information for %d wells' %failures))
add_bro_for_wells.short_description = "BRO registratie gegevens bijwerken voor geselecteerde putten"

def add_bro_for_screens(modeladmin, request, queryset):
    creates = 0
    failures = 0
    updates = 0
    for screen in queryset:
        try:
            query = MonitoringTube.objects.filter(screen=screen)
            if query.exists():
                query.first().update()
                updates += 1
            else:
                MonitoringTube.create_for_screen(screen)
                creates += 1
        except Exception as e:
            failures += 1
    if creates:
        messages.success(request,_('BRO information created for %d screens' %creates)) 
    if updates:
        messages.success(request,_('BRO information updated for %d screens' %updates)) 
    if failures:
        messages.error(request,_('Could not create or update BRO information for %d screens' %failures))
add_bro_for_screens.short_description = "BRO registratie gegevens bijwerken voor geselecteerde filters"
