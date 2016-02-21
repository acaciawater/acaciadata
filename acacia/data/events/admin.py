from django.contrib import admin
from .models import Event, Target, Trigger, History
from django.db import models

class EventAdmin(admin.ModelAdmin):
    model = Event
    list_display=('trigger', 'target', 'action')        

class TargetAdmin(admin.ModelAdmin):
    model = Target
    list_display=('user','email', 'cellphone')        

class TriggerAdmin(admin.ModelAdmin):
    model = Trigger
    list_display=('name', 'series')        

class HistoryAdmin(admin.ModelAdmin):
    model = History
    list_display=('__unicode__', 'user', 'date', 'sent')        

admin.site.register(Trigger,TriggerAdmin)
admin.site.register(Target,TargetAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(History, HistoryAdmin)
