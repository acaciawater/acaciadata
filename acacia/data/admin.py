import os
from .models import Project, ProjectLocatie, MeetLocatie, Datasource, SourceFile, Generator
from .models import Parameter, Series, DataPoint, Chart, ChartSeries, Dashboard, DashboardChart, TabGroup, TabPage
from .models import Variable, Formula, Webcam, Notification, ManualSeries, Grid

from django.shortcuts import render, redirect
from django.contrib import admin
from django import forms
from django.forms import PasswordInput, ModelForm
from django.contrib.gis.db import models
from django.contrib.contenttypes.models import ContentType

import django.contrib.gis.forms as geoforms
import json
import actions

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
    formfield_overrides = {models.TextField: {'widget': forms.Textarea(attrs={'class': 'htmleditor'})}}

class ProjectLocatieForm(ModelForm):
    model = ProjectLocatie
    location = geoforms.PointField(widget=
        geoforms.OSMWidget(attrs={'map_width': 800, 'map_height': 500}))
        
class ProjectLocatieAdmin(admin.ModelAdmin):
    #form = ProjectLocatieForm
    actions = [actions.meetlocatie_aanmaken,]
    list_display = ('name','project','location_count',)
    list_filter = ('project',)
    formfield_overrides = {models.PointField:{'widget': forms.TextInput(attrs={'width': '40px'})},
                           models.TextField: {'widget': forms.Textarea(attrs={'class': 'htmleditor'})}}
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
    formfield_overrides = {models.PointField:{'widget': forms.TextInput, 'required': False},
                           models.TextField: {'widget': forms.Textarea(attrs={'class': 'htmleditor'})}}
    actions = [actions.meteo_toevoegen, 'add_notifications']

    class NotificationActionForm(forms.Form):
        from .models import LOGGING_CHOICES
        email = forms.EmailField(label='Email adres', required=True)
        level = forms.ChoiceField(label='Niveau', choices=LOGGING_CHOICES,required=True)
    
    def add_notifications(self, request, queryset):
        if 'apply' in request.POST:
            form = self.NotificationActionForm(request.POST)   
            if form.is_valid():
                email = form.cleaned_data['email']
                level = form.cleaned_data['level']
                num = 0
                for loc in queryset:
                    for ds in loc.datasources.all():
                        ds.notification_set.add(Notification(user=request.user,email=email,level=level))
                        num += 1
                self.message_user(request, "%d gegevensbronnen getagged" % num)
                return
        elif 'cancel' in request.POST:
            return redirect(request.get_full_path())
        else:
            form = self.NotificationActionForm(initial={'email': request.user.email, 'level': 'ERROR'})
        return render(request,'data/notify.html',{'form': form, 'locaties': queryset, 'check': admin.helpers.ACTION_CHECKBOX_NAME})
    
    add_notifications.short_description='Berichtgeving toevoegen aan geselecteerde meetlocaties'
    
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
    actions = [actions.upload_datasource, actions.update_parameters]
    list_filter = ('meetlocatie','meetlocatie__projectlocatie','meetlocatie__projectlocatie__project','generator')
    list_display = ('name', 'description', 'meetlocatie', 'generator', 'last_download', 'filecount', 'parametercount', 'seriescount', 'start', 'stop', 'rows',)
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
    search_fields = ['name',]

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
    classes = ('grp-collapse grp-closed',)

class SeriesForm(forms.ModelForm):
    model =  Series

    def clean_scale_series(self):
        series = self.cleaned_data['scale_series']
        if series is not None:
            scale = self.cleaned_data['scale']
            if scale != 1:
                raise forms.ValidationError('Als een verschalingtijdreeks is opgegeven moet de verschalingsfactor gelijk aan 1 zijn')
        return series

    def clean_offset_series(self):
        series = self.cleaned_data['offset_series']
        if series is not None:
            offset = self.cleaned_data['offset']
            if offset != 0:
                raise forms.ValidationError('Als een compenmsatietijdreeks is opgegeven moet de compensatiefactor gelijk aan 0 zijn')
        return series

from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin

class SaveUserMixin:
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

class ParameterSeriesAdmin(PolymorphicChildModelAdmin, SaveUserMixin):
    actions = [actions.copy_series, actions.download_series, actions.refresh_series, actions.replace_series, actions.series_thumbnails, actions.update_series_properties, actions.empty_series]
    #list_display = ('name', 'thumbtag', 'parameter', 'datasource', 'unit', 'aantal', 'van', 'tot', 'minimum', 'maximum', 'gemiddelde')
    base_model = Series
    #base_form = SeriesForm
    exclude = ('user',)

    raw_id_fields = ('scale_series','offset_series')
    autocomplete_lookup_fields = {
        'fk': ['scale_series', 'offset_series'],
    }
    search_fields = ['name','parameter__name','parameter__datasource__name']

    fieldsets = (
                 ('Algemeen', {'fields': ('parameter', 'name', ('unit', 'type'), 'description',),
                               'classes': ('grp-collapse grp-open',),
                               }),
                 ('Tijdsinterval', {'fields': ('from_limit','to_limit'),
                               'classes': ('grp-collapse grp-closed',)
                               }),
                 ('Bewerkingen', {'fields': (('resample', 'aggregate',),('scale', 'scale_series'), ('offset','offset_series'), ('cumsum', 'cumstart' ),),
                               'classes': ('grp-collapse grp-closed',),
                              }),
    )

#class ManualSeriesAdmin(admin.ModelAdmin):
class ManualSeriesAdmin(PolymorphicChildModelAdmin, SaveUserMixin):
    base_model = Series
    actions = [actions.copy_series, actions.series_thumbnails]
    #list_display = ('name', 'locatie', 'thumbtag', 'unit', 'aantal', 'van', 'tot', 'minimum', 'maximum', 'gemiddelde')
    exclude = ('user','parameter')
    inlines = [DataPointInline,]
    search_fields = ['name','locatie']
    fieldsets = (
                 ('Algemeen', {'fields': ('locatie', 'name', ('unit', 'type'), 'description',),
                               'classes': ('grp-collapse grp-open',),
                               }),
    )

#class FormulaAdmin(SeriesAdmin):
class FormulaSeriesAdmin(PolymorphicChildModelAdmin, SaveUserMixin):
    base_model = Series
    #list_display = ('name', 'thumbtag', 'locatie', 'unit', 'aantal', 'van', 'tot', 'minimum', 'maximum', 'gemiddelde')
    #search_fields = ['name','locatie']
    
    fieldsets = (
                  ('Algemeen', {'fields': ('locatie', 'name', ('unit', 'type'), 'description',),
                                'classes': ('grp-collapse grp-open',),
                                }),
                 ('Tijdsinterval', {'fields': ('from_limit','to_limit'),
                               'classes': ('grp-collapse grp-closed',)
                               }),
                 ('Bewerkingen', {'fields': (('resample', 'aggregate',),('scale', 'scale_series'), ('offset','offset_series'), ('cumsum', 'cumstart' ),),
                               'classes': ('grp-collapse grp-closed',),
                              }),
                 ('Berekening', {'fields': ('formula_variables', 'intersect', 'formula_text'),
                               'classes': ('grp-collapse grp-closed',),
                              }),
    )
    filter_horizontal = ('formula_variables',)
    #exclude = ('parameter',)
    
#     def clean_formula_text(self):
#         # try to evaluate the expression
#         data = self.cleaned_data['formula_text']
#         try:
#             variables = self.instance.get_variables()
#             eval(data, globals(), variables)
#         except Exception as e:
#             raise forms.ValidationError('Fout bij berekening formule: %s' % e)
#         return data
        
#class SeriesAdmin(admin.ModelAdmin):
class SeriesAdmin(PolymorphicParentModelAdmin):
    actions = [actions.create_grid, actions.copy_series, actions.download_series, actions.refresh_series, actions.replace_series, actions.series_thumbnails, actions.update_series_properties, actions.empty_series]
    list_display = ('name', 'thumbtag', 'typename', 'parameter', 'datasource', 'unit', 'aantal', 'van', 'tot', 'minimum', 'maximum', 'gemiddelde')
    base_model = Series
    #base_form = SeriesForm
    child_models = ((ManualSeries, ManualSeriesAdmin), (Formula, FormulaSeriesAdmin), (Series, ParameterSeriesAdmin))
    exclude = ('user',)

    raw_id_fields = ('scale_series','offset_series')
    autocomplete_lookup_fields = {
        'fk': ['scale_series', 'offset_series'],
    }
    
    class ContentTypeFilter(admin.SimpleListFilter):
        title = 'Tijdreeks type'
        parameter_name = 'ctid'

        def lookups(self, request, modeladmin):
            ''' Possibilities are: series, formula and manual '''
            ct_types = ContentType.objects.get_for_models(Series,Formula,ManualSeries)
            return [(ct.id, ct.name) for ct in sorted(ct_types.values(), key=lambda x: x.name)]

        def queryset(self, request, queryset):
            if self.value() is not None:
                return queryset.filter(polymorphic_ctype_id = self.value())
            return queryset
        
    list_filter = ('parameter__datasource__meetlocatie', 'parameter__datasource', 'parameter__datasource__meetlocatie__projectlocatie__project', ContentTypeFilter)
    search_fields = ['name','parameter__name','parameter__datasource__name']

    base_fieldsets = (
                 ('Algemeen', {'fields': ('parameter', 'name', ('unit', 'type'), 'description',),
                               'classes': ('grp-collapse grp-open',),
                               }),
                 ('Tijdsinterval', {'fields': ('from_limit','to_limit'),
                               'classes': ('grp-collapse grp-closed',)
                               }),
                 ('Bewerkingen', {'fields': (('resample', 'aggregate',),('scale', 'scale_series'), ('offset','offset_series'), ('cumsum', 'cumstart' ),),
                               'classes': ('grp-collapse grp-closed',),
                              }),
    )

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()


class ChartSeriesInline(admin.StackedInline):
    model = ChartSeries
    raw_id_fields = ('series',)
    autocomplete_lookup_fields = {
        'fk': ['series'],
    }
    extra = 0
    fields = (('series', 'order', 'name'), ('axis', 'axislr', 'label'), ('color', 'type', 'stack'), ('t0', 't1'), ('y0', 'y1'))
    ordering = ('order',)

class GridSeriesInline(admin.TabularInline):
    model = ChartSeries
    raw_id_fields = ('series',)
    autocomplete_lookup_fields = {
        'fk': ['series'],
    }
    extra = 1
    fields = ('series', 'order',)
    ordering = ('order',)
    classes = ('grp-collapse grp-closed',)

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

    #formfield_overrides = {models.TextField: {'widget': forms.Textarea(attrs={'class': 'htmleditor'})}}
                
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

class GridAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'tijdreeksen', )
    inlines = [GridSeriesInline,]
    exclude = ('user',)
    fields =('name', 'description', 'title', ('entity', 'unit', 'scale'),('percount', 'perunit',), ('start', 'stop',),('ymin', 'rowheight'),('zmin','zmax'))
    search_fields = ['name','description', 'title']

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

class VariableAdminForm(forms.ModelForm):

    def clean_name(self):
        name = self.cleaned_data["name"]
        try:
            exec("{0}=1".format(name))
        except:
            raise forms.ValidationError('{0} is een ongeldige python variable'.format(name))
        return name

class VariableAdmin(admin.ModelAdmin):
    list_display = ('name', 'locatie', 'series', )
    list_filter = ('locatie',)
    search_fields = ['name','locatie__name']
    readonly_fields = ('thumbtag',)
    form = VariableAdminForm
    
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
      
class NotificationAdmin(admin.ModelAdmin):
    Model = Notification
        
    list_display = ('datasource', 'user', 'email', 'level', 'active')
    list_filter = ('datasource', 'user', 'email', 'level', 'active')
    search_fields = ('datasource', 'user')
    #action_form = LevelActionForm
    #actions = ['set_level']
    
    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            self.exclude = ('user', 'email')
        else:
            self.exclude = ()
        form = super(NotificationAdmin,self).get_form(request,obj,**kwargs)
        return form
    
    def save_model(self, request, obj, form, change):
        if obj.user is None:
            obj.user = request.user
            obj.email = request.user.email
        obj.subject = obj.subject.replace('%(datasource)', obj.datasource.name)
        obj.save()
        
    def set_level(self, request, queryset):
        level = request.POST.get('level')
        queryset.update(level=level)
    set_level.short_description='Niveau aanpassen'
        
admin.site.register(Project, ProjectAdmin, Media = Media)
admin.site.register(ProjectLocatie, ProjectLocatieAdmin, Media = Media)
admin.site.register(MeetLocatie, MeetLocatieAdmin, Media = Media)
admin.site.register(Series, SeriesAdmin)
admin.site.register(Parameter, ParameterAdmin)
admin.site.register(Generator, GeneratorAdmin)
admin.site.register(Datasource, DatasourceAdmin)
admin.site.register(SourceFile, SourceFileAdmin)
#admin.site.register(ChartSeries)
admin.site.register(Chart, ChartAdmin, Media = Media)
admin.site.register(Dashboard, DashAdmin)
admin.site.register(TabGroup, TabGroupAdmin)
admin.site.register(Variable, VariableAdmin)
admin.site.register(Webcam, WebcamAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Grid, GridAdmin)
