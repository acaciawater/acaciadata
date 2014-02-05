from acacia.data.models import Project, ProjectLocatie, MeetLocatie, Series, DataFile, Generator, Parameter, DataPoint
from django.contrib import admin
from django.db import models
from django import forms

class LocatieInline(admin.TabularInline):
    model = ProjectLocatie
    options = {
        'extra': 0,
    }

class MeetlocatieInline(admin.TabularInline):
    model = MeetLocatie

class DataFileInline(admin.TabularInline):
    model = DataFile

class ParameterInline(admin.TabularInline):
    model = Parameter
    extra = 1
    fields = ('name', 'description', 'unit', 'datafile',)

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'locaties', )
    
class ProjectLocatieAdmin(admin.ModelAdmin):
    list_display = ('name','project','meetlocaties',)
    list_filter = ('project',)

class MeetLocatieAdmin(admin.ModelAdmin):
    list_display = ('name','projectlocatie','project',)
    list_filter = ('projectlocatie','projectlocatie__project',)

def upload_datafile(modeladmin, request, queryset):
    for df in queryset:
        if df.url != '':
            df.download()
        
upload_datafile.short_description = "Upload de geselecteerde data files naar de server"

def update_parameters(modeladmin, request, queryset):
    for df in queryset:
        df.update_parameters()

update_parameters.short_description = "Update de parameterlijst van de geselecteerde data files"

class DataFileAdmin(admin.ModelAdmin):
    inlines = [ParameterInline,]
    actions = [upload_datafile, update_parameters]
    exclude = ['meetlocaties',]
    list_display = ('name', 'description', 'filename', 'filesize', 'filedate', 'parameters',)
    fieldsets = (
                 ('Algemeen', {'fields': ('name', 'description', 'file', 'generator',),
                               'classes': ('grp-collapse grp-open',),
                               }),
                 ('Bronnen', {'fields': ('url',),
                               'classes': ('grp-collapse grp-closed',),
                              }),
                 ('Admin', {'fields': ('user',),
                               'classes': ('grp-collapse grp-closed',),
                            })
    )

class GeneratorAdmin(admin.ModelAdmin):
    list_display = ('name', 'classname', 'description')

class ParameterAdmin(admin.ModelAdmin):
    list_filter = ('datafile',)
    list_display = ('name', 'unit', 'description', 'datafile')

def refresh_series(modeladmin, request, queryset):
    for s in queryset:
        s.refresh()
refresh_series.short_description = 'Actualiseer de geselecteerde tijdreeksen'

class ReadonlyTabularInline(admin.TabularInline):
    can_delete = False
    extra = 0
    editable_fields = []
    
    def get_readonly_fields(self, request, obj=None):
        fields = []
        for field in self.model._meta.get_all_field_names():
            if (not field == 'id'):
                if (field not in self.editable_fields):
                    fields.append(field)
        return fields
    
    def has_add_permission(self, request):
        return False
    
class DataPointInline(ReadonlyTabularInline):
    model = DataPoint
        
class SeriesAdmin(admin.ModelAdmin):
    actions = [refresh_series,]
    list_display = ('name', 'parameter', 'datafile', 'unit', 'van', 'tot', 'minimum', 'maximum', 'gemiddelde')
    inlines = [DataPointInline,]
    
class DataPointAdmin(admin.ModelAdmin):
    list_display = ('series', 'date', 'value',)
    list_filter = ('series', )
    ordering = ('series', 'date', )

admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectLocatie, ProjectLocatieAdmin)
admin.site.register(MeetLocatie, MeetLocatieAdmin)
admin.site.register(Series, SeriesAdmin)
admin.site.register(Parameter, ParameterAdmin)
admin.site.register(Generator, GeneratorAdmin)
admin.site.register(DataFile, DataFileAdmin)
admin.site.register(DataPoint, DataPointAdmin)
