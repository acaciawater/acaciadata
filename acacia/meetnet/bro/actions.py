'''
Created on Nov 19, 2019

@author: theo
'''
from .models import GroundwaterMonitoringWell, MonitoringTube
from django.contrib import messages
from django.utils.text import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist

def update_gmw(modeladmin, request, queryset):
    success=0
    for gmw in queryset:
        try:
            gmw.update(user=request.user)
            success += 1
        except Exception as e:
            messages.error(request,_('Could not create or update BRO information for well %(well)s: %(ex)s') % {'well': gmw, 'ex': e})
    if success:
        messages.success(request,_('BRO information updated for %d wells') % success) 
update_gmw.short_description = _('BRO informatie bijwerken voor geselecteerde monitoring putten')

def update_tube(modeladmin, request, queryset):
    success=0
    for tube in queryset:
        try:
            tube.update(user=request.user)
            success += 1
        except Exception as e:
            messages.error(request,_('Could not create or update BRO information for tube %(tube)s: %(ex)s') % {'tube': tube, 'ex': e})
    if success:
        messages.success(request,_('BRO information updated for %d tubes') % success) 
update_tube.short_description = _('BRO informatie bijwerken voor geselecteerde monitoring buizen')
        
def add_bro_for_wells(modeladmin, request, queryset):
    creates = []
    failures = []
    updates = []
    for well in queryset:
        try:
            well.bro.update(user = request.user)
            updates.append(well)
        except ObjectDoesNotExist:
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
add_bro_for_wells.short_description = "BRO registratie gegevens aanmaken/bijwerken voor geselecteerde putten"

def add_bro_for_screens(modeladmin, request, queryset):
    creates = []
    failures = []
    updates = []
    for screen in queryset:
        try:
            screen.bro.update(user=request.user)
            updates.append(screen)
        except ObjectDoesNotExist:
            MonitoringTube.create_for_screen(screen, user=request.user)
            creates.append(screen)
        except Exception as e:
            messages.error(request,_('Could not create or update BRO information for %(screen)s: %(ex)s') % {'screen': screen, 'ex':e})
            failures.append(screen)
    if creates:
        messages.success(request,_('BRO information created for %d screens') % len(creates)) 
    if updates:
        messages.success(request,_('BRO information updated for %d screens') % len(updates)) 
add_bro_for_screens.short_description = "BRO registratie gegevens aanmaken/bijwerken voor geselecteerde filters"
