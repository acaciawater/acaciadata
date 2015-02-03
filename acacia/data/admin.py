import os
from acacia.data.models import Project, ProjectLocatie, MeetLocatie, Datasource, SourceFile, Generator
from acacia.data.models import Parameter, Series, DataPoint, Chart, ChartSeries, Dashboard, DashboardChart, TabGroup, TabPage
from acacia.data.models import Variable, Formula, Webcam, Notification

from django.contrib import admin
from django import forms
from django.forms import PasswordInput, ModelForm
from django.contrib.gis.db import models
import django.contrib.gis.forms as geoforms
import json
import actions
from django.contrib.auth.models import User

class Media:
    js = [
        '/static/grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
        '/static/acacia/js/tinymce_setup/tinymce_setup.js',
    ]
    
class LocatieInline(admin.TabularInline):
    model = ProjectLocatie
    options = {
        'extra': 0,
    }

class MeetlocatieInline(admin.TabularInline):
    model = MeetLocatie

from django.forms.models import BaseInlineFormSet

class SourceInlineFormSet(BaseInlineFormSet):
    def get_queryset(self):
        qs = super(SourceInlineFormSet, self).get_queryset()
        return qs[:100] # limit number of formsets
    
class SourceFileInline(admin.TabularInline):
    model = SourceFile
    exclude = ('cols', 'crc', 'user')
    extra = 0
    ordering = ('-start', '-stop', 'name')
    formset = SourceInlineFormSet
    
class ParameterInline(admin.TabularInline):
    model = Parameter
    extra = 0
    fields = ('name', 'description', 'unit', 'datasource',)

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'location_count', )

class ProjectLocatieForm(ModelForm):
    model = ProjectLocatie
    location = geoforms.PointField(widget=
        geoforms.OSMWidget(attrs={'map_width': 800, 'map_height': 500}))
        
class ProjectLocatieAdmin(admin.ModelAdmin):
    #form = ProjectLocatieForm
    list_display = ('name','project','location_count',)
    list_filter = ('project',)
    formfield_overrides = {models.PointField:{'widget': forms.TextInput(attrs={'size': '40'})}}

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
    formfield_overrides = {models.PointField:{'widget': forms.TextInput, 'required': False}}
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
    
    def clean(self):
        cleaned_data = super(DatasourceForm, self).clean()
        update = self.cleaned_data['autoupdate']
        if update:
            url = self.cleaned_data['url']
            if url == '' or url is None:
                raise forms.ValidationError('Als autoupdate aangevinkt is moet een url opgegeven worden')
        return cleaned_data
        
class DatasourceAdmin(admin.ModelAdmin):
    form = DatasourceForm
    inlines = [SourceFileInline,] # takes VERY long for decagon with more than 1000 files
    search_fields = ['name',]
    actions = [actions.upload_datasource, actions.replace_parameters, actions.update_parameters]
    list_filter = ('meetlocatie','meetlocatie__projectlocatie','meetlocatie__projectlocatie__project',)
    list_display = ('name', 'description', 'meetlocatie', 'last_download', 'filecount', 'parametercount', 'seriescount', 'start', 'stop', 'rows',)
    fieldsets = (
                 ('Algemeen', {'fields': ('name', 'description', 'timezone', 'meetlocatie',),
                               'classes': ('grp-collapse grp-open',),
                               }),
                 ('Bronnen', {'fields': (('generator', 'autoupdate'), 'url',('username', 'password',), 'config',),
                               'classes': ('grp-collapse grp-closed',),
                              }),
    )
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()
        
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            try:
                if instance.user is None:
                    instance.user = request.user
            except:
                    instance.user = request.user
            if instance.name is None or len(instance.name) == 0:
                instance.name,ext = os.path.splitext(os.path.basename(instance.file.name))
            instance.save()
        formset.save_m2m()
        
class GeneratorAdmin(admin.ModelAdmin):
    list_display = ('name', 'classname', 'description')

class SourceFileAdmin(admin.ModelAdmin):
    fields = ('name', 'datasource', 'file',)
    list_display = ('name','datasource', 'meetlocatie', 'filetag', 'rows', 'cols', 'start', 'stop', 'uploaded',)
    list_filter = ('datasource', 'datasource__meetlocatie', 'datasource__meetlocatie__projectlocatie__project', 'uploaded',)
    search_fields = ['name','file__name',]

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()
    
class ParameterAdmin(admin.ModelAdmin):
    list_filter = ('datasource','datasource__meetlocatie', 'datasource__meetlocatie__projectlocatie__project')
    actions = [actions.update_thumbnails, actions.generate_series,]
    list_display = ('name', 'thumbtag', 'meetlocatie', 'datasource', 'unit', 'description', 'seriescount')
#     actions = [actions.generate_series,]
#     list_display = ('name', 'meetlocatie', 'datasource', 'unit', 'description', 'seriescount')    
    search_fields = ['name','description', 'datasource__name']
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
    
class DataPointInline(admin.TabularInline):
    model = DataPoint
    
class SeriesAdmin(admin.ModelAdmin):
    actions = [actions.copy_series, actions.download_series, actions.refresh_series, actions.replace_series, actions.series_thumbnails, actions.update_series_properties, actions.empty_series]
    list_display = ('name', 'thumbtag', 'parameter', 'datasource', 'unit', 'aantal', 'van', 'tot', 'minimum', 'maximum', 'gemiddelde')
    exclude = ('user',)
#    inlines = [DataPointInline,]
    list_filter = ('parameter__datasource__meetlocatie', 'parameter__datasource', 'parameter__datasource__meetlocatie__projectlocatie__project')
    search_fields = ['name','parameter__name','parameter__datasource__name']

    fieldsets = (
                 ('Algemeen', {'fields': ('parameter', 'name', ('unit', 'type'), 'description',),
                               'classes': ('grp-collapse grp-open',),
                               }),
                 ('Bewerkingen', {'fields': (('resample', 'aggregate',),('scale', 'offset',), ('cumsum', 'cumstart' ),),
                               'classes': ('grp-collapse grp-closed',),
                              }),
    )

#     def get_readonly_fields(self, request, obj=None):#         if obj and obj.parameter: 
#             self.inlines = []
#             return self.readonly_fields
#         else:
#             return self.readonly_fields  
          
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

class FormulaAdmin(SeriesAdmin):
    list_display = ('name', 'thumbtag', 'locatie', 'unit', 'aantal', 'van', 'tot', 'minimum', 'maximum', 'gemiddelde')
    search_fields = ['name',]
    
    fieldsets = (
                 ('Algemeen', {'fields': ('locatie', 'name', ('unit', 'type'), 'description',),
                               'classes': ('grp-collapse grp-open',),
                               }),
                 ('Bewerkingen', {'fields': (('resample', 'aggregate',),('scale', 'offset',), ('cumsum', 'cumstart' ),),
                               'classes': ('grp-collapse grp-closed',),
                              }),
                 ('Berekening', {'fields': ('formula_variables', 'intersect', 'formula_text'),
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
    fields = (('series', 'order', 'name'), ('axis', 'axislr', 'label'), ('color', 'type', 'stack'), ('t0', 't1'), ('y0', 'y1'))
    ordering = ('order',)
    
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
    search_fields = ['name','description', 'title']

    formfield_overrides = {models.TextField: {'widget': forms.Textarea(attrs={'class': 'htmleditor'})}}
                
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()
        
class ChartInline(admin.TabularInline):
    model = DashboardChart
    extra = 0
    ordering = ('order',)
    
class DashAdmin(admin.ModelAdmin):
    filter_horizontal = ('charts',)
    list_display = ('name', 'description', 'grafieken',)
    exclude = ('user',)
    search_fields = ['name','description']
    inlines = [ChartInline,]
        
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

class VariableAdmin(admin.ModelAdmin):
    list_display = ('name', 'locatie', 'series', )
    list_filter = ('locatie',)
    search_fields = ['name','locatie__name']

class TabPageAdmin(admin.ModelAdmin):
    list_display = ('name', 'tabgroup', 'order', 'dashboard',)
    list_filter = ('tabgroup',)
    search_fields = ['name',]

class TabPageInline(admin.TabularInline):
    model = TabPage
    fields = ('name', 'tabgroup', 'order', 'dashboard',)
    extra = 0
    
class TabGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'pagecount')
    search_fields = ['name',]
    list_filter = ('location',)
    inlines = [TabPageInline,]
    
class WebcamAdmin(admin.ModelAdmin):
    list_display = ('name', 'snapshot', )

class NotificationForm(ModelForm):
    model = Notification
    
    def __init__(self, *args, **kwargs):
        #kwargs['initial'].update({'description': get_default_content()})
        super(NotificationForm, self).__init__(*args, **kwargs)
      
class NotificationAdmin(admin.ModelAdmin):
    Model = Notification
    #exclude = ('user','email')
    #form = NotificationForm
    
#     def get_prepopulated_fields(self, request, obj=None):
#         if request is not None:
#             self.user = request.user
#             self.email = self.user.email
#         return self.prepopulated_fields
    #def formfield_for_db_field(self):
        
    def get_form(self, request, obj=None, **kwargs):
        form = super(NotificationAdmin,self).get_form(request,obj,**kwargs)
        if obj is None:
            user = request.user
            email = request.user.email
            if hasattr(form,'initial'):
                initial = form.initial
            else:
                initial = {}
            initial.update({'user': user, 'email': email})
            form.initial = initial
        return form
    
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.email = request.user.email
        obj.save()
        
admin.site.register(Project, ProjectAdmin, Media = Media)
admin.site.register(ProjectLocatie, ProjectLocatieAdmin, Media = Media)
admin.site.register(MeetLocatie, MeetLocatieAdmin)
admin.site.register(Series, SeriesAdmin)
admin.site.register(Parameter, ParameterAdmin)
admin.site.register(Generator, GeneratorAdmin)
admin.site.register(Datasource, DatasourceAdmin)
admin.site.register(SourceFile, SourceFileAdmin)
#admin.site.register(DataPoint, DataPointAdmin)
admin.site.register(Chart, ChartAdmin, Media = Media)
admin.site.register(Dashboard, DashAdmin)
admin.site.register(TabGroup, TabGroupAdmin)
admin.site.register(TabPage, TabPageAdmin)
admin.site.register(Formula, FormulaAdmin)
admin.site.register(Variable, VariableAdmin)
admin.site.register(Webcam, WebcamAdmin)
admin.site.register(Notification, NotificationAdmin)
