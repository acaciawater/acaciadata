from acacia.data.models import Project, ProjectLocatie, MeetLocatie, Datasource, SourceFile, Generator
from acacia.data.models import Parameter, Series, DataPoint, Chart, ChartSeries, Dashboard
from acacia.data.models import Variable, Formula

from django.contrib import admin
from django import forms
from django.forms import PasswordInput, ModelForm
from django.contrib.gis.db import models
from django.forms.widgets import Textarea
import django.contrib.gis.forms as geoforms
import json
import actions

class LocatieInline(admin.TabularInline):
    model = ProjectLocatie
    options = {
        'extra': 0,
    }

class MeetlocatieInline(admin.TabularInline):
    model = MeetLocatie

class SourceFileInline(admin.TabularInline):
    model = SourceFile
    exclude = ('cols', 'crc', 'user')
    extra = 0
    ordering = ('-start', '-stop', 'name',)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()
    
class ParameterInline(admin.TabularInline):
    model = Parameter
    extra = 0
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
    
class MeetLocatieAdmin(admin.ModelAdmin):
    form = MeetLocatieForm
    list_display = ('name','projectlocatie','project','datasourcecount',)
    list_filter = ('projectlocatie','projectlocatie__project',)
    formfield_overrides = {models.PointField:{'widget': Textarea, 'required': False}}
    actions = [actions.meteo_toevoegen]
    
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
    actions = [actions.upload_datasource, actions.replace_parameters, actions.update_parameters]
    list_filter = ('meetlocatie','meetlocatie__projectlocatie','meetlocatie__projectlocatie__project',)
    list_display = ('name', 'description', 'meetlocatie', 'last_download', 'filecount', 'parametercount', 'seriescount', 'start', 'stop', 'rows',)
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

class SourceFileAdmin(admin.ModelAdmin):
    fields = ('name', 'datasource', 'file',)
    list_display = ('name','datasource', 'meetlocatie', 'filetag', 'rows', 'cols', 'start', 'stop', 'uploaded',)
    list_filter = ('datasource', 'datasource__meetlocatie', 'uploaded',)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()
    
class ParameterAdmin(admin.ModelAdmin):
    list_filter = ('datasource','datasource__meetlocatie',)
    actions = [actions.update_thumbnails, actions.generate_series,]
    list_display = ('name', 'thumbtag', 'meetlocatie', 'datasource', 'unit', 'description', 'seriescount')
    ordering = ('name','datasource',)

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
    actions = [actions.copy_series, actions.download_series, actions.refresh_series, actions.replace_series, actions.series_thumbnails]
    list_display = ('name', 'thumbtag', 'parameter', 'datasource', 'unit', 'aantal', 'van', 'tot', 'minimum', 'maximum', 'gemiddelde')
    exclude = ('user',)
    list_filter = ('parameter__datasource__meetlocatie', 'parameter__datasource')

    fieldsets = (
                 ('Algemeen', {'fields': ('parameter', 'name', 'unit', 'description',),
                               'classes': ('grp-collapse grp-open',),
                               }),
                 ('Bewerkingen', {'fields': (('resample', 'aggregate',),('scale', 'offset',), ('cumsum', 'cumstart' ),),
                               'classes': ('grp-collapse grp-closed',),
                              }),
    )

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()


class FormulaAdmin(SeriesAdmin):
    list_display = ('name', 'thumbtag', 'locatie', 'unit', 'aantal', 'van', 'tot', 'minimum', 'maximum', 'gemiddelde')
    
    fieldsets = (
                 ('Algemeen', {'fields': ('locatie', 'name', 'unit', 'description',),
                               'classes': ('grp-collapse grp-open',),
                               }),
                 ('Bewerkingen', {'fields': (('resample', 'aggregate',),('scale', 'offset',), ('cumsum', 'cumstart' ),),
                               'classes': ('grp-collapse grp-closed',),
                              }),
                 ('Berekening', {'fields': ('formula_variables', 'formula_text'),
                               'classes': ('grp-collapse grp-closed',),
                              }),
    )
    filter_horizontal = ('formula_variables',)
    exclude = ('parameter',)
    
#     def save_model(self, request, obj, form, change):
#         # TODO: allow null value for parameter
#         obj.parameter = Parameter.objects.first()
#         return super(FormulaAdmin, self).save_model(request, obj, form, change)
    
class ChartSeriesInline(admin.StackedInline):
    model = ChartSeries
    extra = 0
        
class DataPointAdmin(admin.ModelAdmin):
    list_display = ('series', 'date', 'value',)
    list_filter = ('series', )
    ordering = ('series', 'date', )

class ChartAdmin(admin.ModelAdmin):
    actions = [actions.copy_charts,]
    list_display = ('name', 'title', 'tijdreeksen', )
    inlines = [ChartSeriesInline,]
    exclude = ('user',)
    fields = ('name', 'description', 'title', ('percount', 'perunit',), ('start', 'stop',),)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()
    
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
#admin.site.register(DataPoint, DataPointAdmin)
admin.site.register(Chart, ChartAdmin)
admin.site.register(Dashboard, DashAdmin)
admin.site.register(Formula, FormulaAdmin)
admin.site.register(Variable)
