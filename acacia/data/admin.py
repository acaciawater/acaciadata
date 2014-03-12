from acacia.data.models import Project, ProjectLocatie, MeetLocatie, Series, Datasource, SourceFile, Generator, Parameter, DataPoint, Chart, Dashboard
from acacia.data.shortcuts import meteo2locatie
from django.contrib import admin
from django import forms
from django.forms import PasswordInput, ModelForm
from django.contrib.gis.db import models
from django.forms.widgets import Textarea
import django.contrib.gis.forms as geoforms
import json
import logging
logger = logging.getLogger(__name__)

class LocatieInline(admin.TabularInline):
    model = ProjectLocatie
    options = {
        'extra': 0,
    }

class MeetlocatieInline(admin.TabularInline):
    model = MeetLocatie

class SourceFileInline(admin.TabularInline):
    model = SourceFile
    exclude = ('cols', 'crc', 'user', )
    extra = 0
    ordering = ('-start', '-stop', 'name',)
    
class ParameterInline(admin.TabularInline):
    model = Parameter
    extra = 1
    fields = ('name', 'description', 'unit', 'datasource',)

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'location_count', )

class ProjectLocatieForm(ModelForm):
    model = ProjectLocatie
    point = geoforms.PointField(widget=
        geoforms.OSMWidget(attrs={'map_width': 800, 'map_height': 500}))
        
class ProjectLocatieAdmin(admin.ModelAdmin):
    #form = ProjectLocatieForm
    list_display = ('name','project','location_count',)
    list_filter = ('project',)
    formfield_overrides = {models.PointField:{'widget': Textarea}}

class MeetLocatieForm(ModelForm):
    
    def clean_location(self):
        loc = self.cleaned_data['location']
        if loc is None:
            # set default location
            projectloc = self.cleaned_data['projectlocatie']
            loc = projectloc.location
        return loc
    
    def clean_name(self):
        # trim whitespace from name
        return self.cleaned_data['name'].strip()
    
def meteo_toevoegen(modeladmin, request, queryset):
    for loc in queryset:
        meteo2locatie(loc,user=request.user)
meteo_toevoegen.short_description = "Meteostation, neerslagstation en regenradar toevoegen"
    
class MeetLocatieAdmin(admin.ModelAdmin):
    form = MeetLocatieForm
    list_display = ('name','projectlocatie','project','datasourcecount',)
    list_filter = ('projectlocatie','projectlocatie__project',)
    formfield_overrides = {models.PointField:{'widget': Textarea, 'required': False}}
    actions = [meteo_toevoegen]
    
def upload_datasource(modeladmin, request, queryset):
    for df in queryset:
        if df.url != '':
            df.download()
upload_datasource.short_description = "Upload de geselecteerde datasources naar de server"

def update_parameters(modeladmin, request, queryset):
    for df in queryset:
        df.update_parameters()
update_parameters.short_description = "Update de parameterlijst van de geselecteerde datasources"

def replace_parameters(modeladmin, request, queryset):
    for df in queryset:
        count = df.parametercount()
        df.parameter_set.all().delete()
        logger.info('%d parameters deleted for datasource %s' % (count or 0, df))
        df.update_parameters()    
replace_parameters.short_description = "Vervang de parameterlijst van de geselecteerde datasources"

class DatasourceForm(ModelForm):
    model = Datasource
    password = forms.CharField(label='Wachtwoord', help_text='Wachtwoord voor de webservice', widget=PasswordInput(render_value=True),required=False)

    def clean_config(self):
        config = self.cleaned_data['config']
        try:
            if config != '':
                json.loads(config)
        except Exception as ex:
            raise forms.ValidationError('Onjuiste JSON dictionary: %s'% ex)
        return config
    
class DatasourceAdmin(admin.ModelAdmin):
    form = DatasourceForm
#    inlines = [ParameterInline,]
    inlines = [SourceFileInline,]
    actions = [upload_datasource, replace_parameters]
    list_filter = ('meetlocatie','meetlocatie__projectlocatie','meetlocatie__projectlocatie__project',)
    list_display = ('name', 'description', 'meetlocatie', 'filecount', 'parametercount', 'seriescount', 'start', 'stop', 'rows',)
    fieldsets = (
                 ('Algemeen', {'fields': ('name', 'description', 'meetlocatie',),
                               'classes': ('grp-collapse grp-open',),
                               }),
                 ('Bronnen', {'fields': ('generator', 'url',('username', 'password'), 'config',),
                               'classes': ('grp-collapse grp-closed',),
                              }),
    )
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

class GeneratorAdmin(admin.ModelAdmin):
    list_display = ('name', 'classname', 'description')

def update_thumbnails(modeladmin, request, queryset):
    # group queryset by datasource
    group = {}
    for p in queryset:
        if not p.datasource in group:
            group[p.datasource] = []
        group[p.datasource].append(p)
         
    for fil,parms in group.iteritems():
        data = fil.get_data()
        for p in parms:
            p.make_thumbnail(data=data)
            p.save()
    
update_thumbnails.short_description = "Thumbnails vernieuwen van geselecteerde parameters"

def generate_series(modeladmin, request, queryset):
    for p in queryset:
        try:
            s, created = p.series_set.get_or_create(name = p.name, description = p.description, unit = p.unit, type = p.type, user = request.user)
            s.replace()
            s.make_thumbnail() 
            s.save()
        except Exception as e:
            logger.error('ERROR creating series %s: %s' % (p.name, e))
generate_series.short_description = 'Standaard tijdreeksen aanmaken voor geselecteerde parameters'

class SourceFileAdmin(admin.ModelAdmin):
    fields = ('name', 'datasource', 'file',)
    list_display = ('name','datasource', 'meetlocatie', 'filetag', 'rows', 'cols', 'start', 'stop', 'uploaded',)
    list_filter = ('datasource', 'datasource__meetlocatie', 'uploaded',)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()
    
class ParameterAdmin(admin.ModelAdmin):
    list_filter = ('datasource','datasource__meetlocatie',)
    actions = [update_thumbnails,generate_series,]
    list_display = ('name', 'thumbtag', 'meetlocatie', 'datasource', 'unit', 'description', 'seriescount')
    ordering = ('name','datasource',)
    
def download_series(queryset):
    ds = set([series.datasource() for series in queryset])
    for d in ds:
        d.download()
    
def refresh_series(modeladmin, request, queryset):
    download_series(queryset)
    for s in queryset:
        s.update()
refresh_series.short_description = 'Geselecteerde tijdreeksen actualiseren'

def replace_series(modeladmin, request, queryset):
    download_series(queryset)
    for s in queryset:
        s.replace()
replace_series.short_description = 'Geselecteerde tijdreeksen opnieuw aanmaken'

def series_thumbnails(modeladmin, request, queryset):
    for s in queryset:
        s.make_thumbnail()
        s.save()
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
    list_display = ('name', 'thumbtag', 'parameter', 'datasource', 'unit', 'aantal', 'van', 'tot', 'minimum', 'maximum', 'gemiddelde')
    exclude = ('user',)
    list_filter = ('parameter__datasource__meetlocatie',)

    fieldsets = (
                 ('Algemeen', {'fields': ('parameter', 'name', 'unit', 'description',),
                               'classes': ('grp-collapse grp-open',),
                               }),
                 ('Grafiek opties', {'fields': ('axis', 'axislr', 'label', 'color','type', 'y0', 'y1', 't0', 't1',),
                               'classes': ('grp-collapse grp-closed',),
                              }),
    )

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()
 
class SeriesInline(admin.TabularInline):
    model = Series
        
class DataPointAdmin(admin.ModelAdmin):
    list_display = ('series', 'date', 'value',)
    list_filter = ('series', )
    ordering = ('series', 'date', )

def copy_charts(modeladmin, request, queryset):
    user = request.user
    for c in queryset:
        name = 'kopie van %s' % (c.name)
        copy = 1 
        while Chart.objects.filter(name = name).exists():
            copy += 1
            name = 'kopie %d van %s' % (copy, c.name)
        c.pk = None
        c.name = name
        c.user = request.user
        c.save()
copy_charts.short_description = "Geselecteerde grafieken dupliceren"

class ChartAdmin(admin.ModelAdmin):
    filter_horizontal = ('series',)
    actions = [copy_charts,]
    list_display = ('name', 'title', 'tijdreeksen', )

class DashAdmin(admin.ModelAdmin):
    filter_horizontal = ('charts',)
    list_display = ('name', 'description', 'grafieken',)
    exclude = ('user',)
    
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()
    
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectLocatie, ProjectLocatieAdmin)
admin.site.register(MeetLocatie, MeetLocatieAdmin)
admin.site.register(Series, SeriesAdmin)
admin.site.register(Parameter, ParameterAdmin)
admin.site.register(Generator, GeneratorAdmin)
admin.site.register(Datasource, DatasourceAdmin)
admin.site.register(SourceFile, SourceFileAdmin)
admin.site.register(DataPoint, DataPointAdmin)
admin.site.register(Chart, ChartAdmin)
admin.site.register(Dashboard, DashAdmin)
