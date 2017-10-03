from django.contrib import admin

# Register your models here.
from .models import AHN

def test_ahn(modeladmin, request, queryset):
    for a in queryset:
        z = a.get_elevation(108526,448330)
        print a, z
        
@admin.register(AHN)
class AHNAdmin(admin.ModelAdmin):
    actions = [test_ahn]

