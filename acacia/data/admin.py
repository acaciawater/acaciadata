from acacia.data.models import Project, ProjectLocatie, MeetLocatie, Series, DataFile, Generator, Parameter, DataPoint, Chart, ChartOptions, Dashboard
from django.contrib import admin
from django import forms
from django.forms import PasswordInput, ModelForm
import logging
logger = logging.getLogger(__name__)

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
    list_display = ('name', 'locatiecount', )
    
class ProjectLocatieAdmin(admin.ModelAdmin):
    list_display = ('name','project','meetlocaties',)
    list_filter = ('project',)

class MeetDataInline(admin.TabularInline):
    model = MeetLocatie.datafiles.through
    
class MeetLocatieAdmin(admin.ModelAdmin):
    list_display = ('name','projectlocatie','project','filecount',)
    list_filter = ('projectlocatie','projectlocatie__project',)
    #filter_horizontal = ('datafiles',)
    exclude = ('datafiles',)
    inlines = [MeetDataInline,]
    
def upload_datafile(modeladmin, request, queryset):
    for df in queryset:
        if df.url != '':
            df.download()
upload_datafile.short_description = "Upload de geselecteerde data files naar de server"

def update_parameters(modeladmin, request, queryset):
    for df in queryset:
        df.update_parameters()

update_parameters.short_description = "Update de parameterlijst van de geselecteerde data files"

def replace_parameters(modeladmin, request, queryset):
    for df in queryset:
        count = df.parameters()
        df.parameter_set.all().delete()
        logger.info('%d parameters deleted for datafile %s' % (count, df))
        df.update_parameters()
    
replace_parameters.short_description = "Vervang de parameterlijst van de geselecteerde data files"

class DataFileForm(ModelForm):
    model = DataFile
    password = forms.CharField(label='Wachtwoord', help_text='Wachtwoord voor de webservice', widget=PasswordInput(render_value=True),required=False)
    #widgets = {'password': PasswordInput(render_value=False)}
    
class DataFileAdmin(admin.ModelAdmin):
    form = DataFileForm
    inlines = [ParameterInline,]
    actions = [upload_datafile, replace_parameters]
    list_display = ('name', 'description', 'filename', 'filesize', 'filedate', 'parameters',)
    fieldsets = (
                 ('Algemeen', {'fields': ('name', 'description', 'file', 'generator',),
                               'classes': ('grp-collapse grp-open',),
                               }),
                 ('Bronnen', {'fields': ('url',('username', 'password'), 'config',),
                               'classes': ('grp-collapse grp-closed',),
                              }),
                 ('Admin', {'fields': ('user',),
                               'classes': ('grp-collapse grp-closed',),
                            })
    )

class GeneratorAdmin(admin.ModelAdmin):
    list_display = ('name', 'classname', 'description')

def update_thumbnails(modeladmin, request, queryset):
#     for p in queryset:
#         p.save()
    # group queryset by datafile
    group = {}
    for p in queryset:
        if not p.datafile in group:
            group[p.datafile] = []
        group[p.datafile].append(p)
         
    for fil,parms in group.iteritems():
        data = fil.get_data()
        for p in parms:
            p.make_thumbnail(data=data)
            p.save()
    
update_thumbnails.short_description = "Thumbnails vernieuwen"

class ParameterAdmin(admin.ModelAdmin):
    list_filter = ('datafile',)
    actions = [update_thumbnails,]
    list_display = ('name', 'thumbtag', 'datafile', 'unit', 'description')

def refresh_series(modeladmin, request, queryset):
    for s in queryset:
        s.update()
refresh_series.short_description = 'Geselecteerde tijdreeksen actualiseren'

def replace_series(modeladmin, request, queryset):
    for s in queryset:
        s.replace()
replace_series.short_description = 'Geselecteerde tijdreeksen opnieuw aanmaken'

def series_thumbnails(modeladmin, request, queryset):
    for s in queryset:
        s.make_thumbnail()
        s.save() # saving a series will update the thumbnail
series_thumbnails.short_description = "Thumbnails van tijdreeksen vernieuwen"

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
    actions = [refresh_series, replace_series, series_thumbnails]
    list_display = ('name', 'thumbtag', 'parameter', 'datafile', 'unit', 'aantal', 'van', 'tot', 'minimum', 'maximum', 'gemiddelde')

class SeriesInline(admin.TabularInline):
    model = Series
        
class DataPointAdmin(admin.ModelAdmin):
    list_display = ('series', 'date', 'value',)
    list_filter = ('series', )
    ordering = ('series', 'date', )

class ChartAdmin(admin.ModelAdmin):
    filter_horizontal = ('series',)
    list_display = ('name', 'title', 'tijdreeksen', )

class DashAdmin(admin.ModelAdmin):
    filter_horizontal = ('charts',)
    list_filter = ('user', )
    list_display = ('name', 'description', 'grafieken', 'user' )
    
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectLocatie, ProjectLocatieAdmin)
admin.site.register(MeetLocatie, MeetLocatieAdmin)
admin.site.register(Series, SeriesAdmin)
admin.site.register(Parameter, ParameterAdmin)
admin.site.register(Generator, GeneratorAdmin)
admin.site.register(DataFile, DataFileAdmin)
admin.site.register(DataPoint, DataPointAdmin)
admin.site.register(Chart, ChartAdmin)
admin.site.register(ChartOptions)
admin.site.register(Dashboard, DashAdmin)
