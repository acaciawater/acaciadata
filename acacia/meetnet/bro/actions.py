'''
Created on Nov 19, 2019

@author: theo
'''
from .models import GroundwaterMonitoringWell, MonitoringTube
from django.contrib import messages
from django.utils.text import ugettext_lazy as _

def add_bro_for_wells(modeladmin, request, queryset):
    creates = []
    failures = []
    updates = []
    for well in queryset:
        try:
            query = GroundwaterMonitoringWell.objects.filter(well=well)
            if query.exists():
                query.first().update()
                updates.append(well)
            else:
                GroundwaterMonitoringWell.create_for_well(well, user=request.user)
                creates.append(well)
        except Exception as e:
            messages.error(request,_('Could not create or update BRO information for %(well)s: %(ex)s') % {'well': well, 'ex': e})
            failures.append(well)
#     if failures:
#         messages.error(request,_('Could not create or update BRO information for %s wells') % len(failures))
    if creates:
        messages.success(request,_('BRO information created for %d wells') % len(creates)) 
    if updates:
        messages.success(request,_('BRO information updated for %d wells') % len(updates)) 
add_bro_for_wells.short_description = "BRO registratie gegevens bijwerken voor geselecteerde putten"

def add_bro_for_screens(modeladmin, request, queryset):
    creates = []
    failures = []
    updates = []
    for screen in queryset:
        try:
            query = MonitoringTube.objects.filter(screen=screen)
            if query.exists():
                query.first().update()
                updates.append(screen)
            else:
                MonitoringTube.create_for_screen(screen, user=request.user)
                creates.append(screen)
        except Exception as e:
            messages.error(request,_('Could not create or update BRO information for %(screen)s: %(ex)s') % {'screen': screen, 'ex':e})
            failures.append(screen)
    if creates:
        messages.success(request,_('BRO information created for %d screens') % len(creates)) 
    if updates:
        messages.success(request,_('BRO information updated for %d screens') % len(updates)) 

add_bro_for_screens.short_description = "BRO registratie gegevens bijwerken voor geselecteerde filters"
