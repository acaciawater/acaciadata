from acacia.data.models import Project, ProjectLocatie, MeetLocatie, Series, DataFile, Generator, Parameter
from django.contrib import admin

class LocatieInline(admin.TabularInline):
    model = ProjectLocatie
    options = {
        'extra': 0,
    }

class MeetlocatieInline(admin.TabularInline):
    model = MeetLocatie

class DataFileInline(admin.TabularInline):
    model = DataFile

class ParameterInline(admin.StackedInline):
    model = Parameter
    extra = 1

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

def update_parameters(modeladmin, reuest, queryset):
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
                 ('Bronnen', {'fields': ('url','autorefresh',),
                               'classes': ('grp-collapse grp-closed',),
                              }),
                 ('Admin', {'fields': ('user',),
                               'classes': ('grp-collapse grp-closed',),
                            })
    )

class DataProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'classname', 'description')

class ParameterAdmin(admin.ModelAdmin):
    list_filter = ('datafile',)
    list_display = ('name', 'unit', 'description', )
    
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectLocatie, ProjectLocatieAdmin)
admin.site.register(MeetLocatie, MeetLocatieAdmin)
admin.site.register(Series)
admin.site.register(Parameter, ParameterAdmin)
admin.site.register(Generator)
admin.site.register(DataFile, DataFileAdmin)
