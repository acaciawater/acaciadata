import os
from .models import Project, ProjectLocatie, MeetLocatie, Datasource, SourceFile, Generator
from .models import Parameter, Series, DataPoint, Chart, ChartSeries, Dashboard, DashboardChart, TabGroup, TabPage
from .models import Variable, Formula, Webcam, Notification, ManualSeries, Grid, CalibrationData, KeyFigure

from django.shortcuts import render, redirect
from django.contrib import admin
from django import forms
from django.forms import PasswordInput, ModelForm
from django.contrib.gis.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _

import django.contrib.gis.forms as geoforms
import json
import actions
from acacia.data.models import PlotLine, LineStyle, PlotBand, BandStyle
import dateutil
    
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
        return qs[:10] # limit number of formsets

class SourceFileInline(admin.TabularInline):
    model = SourceFile
    exclude = ('cols', 'crc', 'user')
    extra = 0
    ordering = ('-start', '-stop', 'name')
    classes = ('grp-collapse grp-closed',)
    formset = SourceInlineFormSet

class ParameterInline(admin.TabularInline):
    model = Parameter
    extra = 0
    fields = ('name', 'description', 'unit', 'datasource',)

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'location_count', )
    exclude = ['image']
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
    search_fields = ['name',]
    exclude = ['image']
    formfield_overrides = {models.PointField:{'widget': forms.TextInput(attrs={'width': '40px'})},
                           models.TextField: {'widget': forms.Textarea(attrs={'class': 'htmleditor'})}}

class CalibrationAdmin(admin.ModelAdmin):
    model = CalibrationData
    list_display = ('parameter', 'sensor_value', 'calib_value')
    list_filter = ('datasource', 'parameter')
    
class CalibrationInline(admin.TabularInline):
    model = CalibrationData
    extra = 0
    classes = ('grp-collapse grp-closed',)
 
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(CalibrationInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'parameter':
            if request.source is not None:
                field.queryset = field.queryset.filter(datasource__exact = request.source)  
            else:
                field.queryset = field.queryset.none()
        return field 
               
class DatasourceForm(ModelForm):
    model = Datasource
    password = forms.CharField(label=_('password'), help_text=_('password for webservice'), widget=PasswordInput(render_value=True),required=False)

    def clean_config(self):
        config = self.cleaned_data['config']
        try:
            if config != '':
                json.loads(config)
        except Exception as ex:
            raise forms.ValidationError(_('Invalid JSON dictionary: %s') % ex)
        return config
    
#     def clean(self):
#         cleaned_data = super(DatasourceForm, self).clean()
#         update = self.cleaned_data['autoupdate']
#         if update:
#             url = self.cleaned_data['url']
#             if url == '' or url is None:
#                 raise forms.ValidationError('Als autoupdate aangevinkt is moet een url opgegeven worden')
#         return cleaned_data
        
class DatasourceAdmin(admin.ModelAdmin):
    form = DatasourceForm
    inlines = [CalibrationInline, SourceFileInline] # takes VERY long for decagon with more than 1000 files
    search_fields = ['name',]
    actions = [actions.upload_datasource, actions.update_parameters, actions.datasource_dimensions,actions.generate_locations,actions.generate_datasource_series,actions.update_datasource_series]
    list_filter = ('meetlocatie','meetlocatie__projectlocatie','meetlocatie__projectlocatie__project','generator')
    list_display = ('name', 'description', 'meetlocatie', 'generator', 'last_download', 'filecount', 'locationcount', 'parametercount', 'seriescount', 'calibcount','timezone','start', 'stop', 'rows',)
    fieldsets = (
                 ('Algemeen', {'fields': ('name', 'description', 'timezone', 'meetlocatie','locations'),
                               'classes': ('grp-collapse grp-open',),
                               }),
                 ('Bronnen', {'fields': (('generator', 'autoupdate'), 'url',('username', 'password',), 'config',),
                               'classes': ('grp-collapse grp-closed',),
                              }),
    )
    filter_horizontal = ('locations',)
    
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()
        
    def get_form(self, request, obj=None, **kwargs):
        # just save obj reference for future processing in Inline
        request.source = obj
        return super(DatasourceAdmin, self).get_form(request, obj, **kwargs)
     
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, SourceFile):
                try:
                    if instance.user is None:
                        instance.user = request.user
                except:
                        instance.user = request.user
                if instance.name is None or len(instance.name) == 0:
                    instance.name,ext = os.path.splitext(os.path.basename(instance.file.name))
            instance.save()

        # explicitly delete forms marked with 'delete'
        for obj in formset.deleted_objects:
            obj.delete()
            
        formset.save_m2m()

#     def formfield_for_manytomany(self, db_field, request, **kwargs):
#             if db_field.name == 'locations':
#                 kwargs['queryset'] = MeetLocatie.objects.all()
#             return super(DatasourceAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)
            
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

from .models import LOGGING_CHOICES

class MeetLocatieAdmin(admin.ModelAdmin):
    form = MeetLocatieForm
    list_display = ('name','projectlocatie','project','datasourcecount',)
    list_filter = ('projectlocatie','projectlocatie__project',)
    exclude = ['image']
    search_fields = ('name',)

    formfield_overrides = {models.PointField:{'widget': forms.TextInput, 'required': False},
                           models.TextField: {'widget': forms.Textarea(attrs={'class': 'htmleditor'})}}
    actions = [actions.meteo_toevoegen, 'add_notifications', actions.set_locatie]

    class NotificationActionForm(forms.Form):
        email = forms.EmailField(label=_('Email address'), required=True)
        level = forms.ChoiceField(label=_('Level'), choices=LOGGING_CHOICES,required=True)

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
                self.message_user(request, _("%d datasources were tagged") % num)
                return
        elif 'cancel' in request.POST:
            return redirect(request.get_full_path())
        else:
            form = self.NotificationActionForm(initial={'email': request.user.email, 'level': 'ERROR'})
        return render(request,'data/notify.html',{'form': form, 'locaties': queryset, 'check': admin.helpers.ACTION_CHECKBOX_NAME})

    add_notifications.short_description=_('Add email notification to selected datasources')

class NotificationAdmin(admin.ModelAdmin):
    Model = Notification
    actions = ['set_level']
    list_display = ('datasource', 'meetlocatie', 'user', 'email', 'level', 'active')
    list_filter = ('datasource__meetlocatie','datasource', 'user', 'level')
    search_fields = ('datasource', 'user')
    #action_form = LevelActionForm
    #actions = ['set_level']

    class NotificationLevelForm(forms.Form):
        level = forms.ChoiceField(choices = LOGGING_CHOICES, label=_('Level'), initial={'level': 'ERROR'}, required=True, help_text=_('Level of notification'))
    
    def set_level(self, request, queryset):
        if 'apply' in request.POST:
            form = self.NotificationLevelForm(request.POST)   
            if form.is_valid():
                level = form.cleaned_data['level']
                num_updated = queryset.update(level=level)
                self.message_user(request, _("% email notifications changed") % num_updated)
                return
        elif 'cancel' in request.POST:
            return redirect(request.get_full_path())
        else:
            form = self.NotificationLevelForm(initial={'level': 'ERROR'})
        return render(request,'data/change_notify_level.html',{'form': form, 'locaties': queryset, 'check': admin.helpers.ACTION_CHECKBOX_NAME})

    set_level.short_description=_('Change notification level')

    
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
        obj.subject = obj.subject.replace('%(datasource)', obj.source.name)
        obj.save()
        
class GeneratorAdmin(admin.ModelAdmin):
    list_display = ('name', 'classname', 'description','url')

class SourceFileAdmin(admin.ModelAdmin):
    actions = [actions.sourcefile_dimensions,]
    fields = ('name', 'datasource', 'file',)
    list_display = ('name','datasource', 'meetlocatie', 'filetag', 'locs', 'rows', 'cols', 'start', 'stop', 'created',)
    list_filter = ('datasource', 'datasource__meetlocatie', 'datasource__meetlocatie__projectlocatie__project', 'created',)
    search_fields = ['name','datasource__name', 'datasource__meetlocatie__name']

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

class ParameterAdmin(admin.ModelAdmin):
    list_filter = ('datasource','datasource__generator','datasource__meetlocatie', 'datasource__meetlocatie__projectlocatie__project')
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
    ordering = ['date']
    classes = ('grp-collapse grp-open',)
    extra = 0

class SeriesForm(forms.ModelForm):
    model =  Series

    def clean_scale_series(self):
        series = self.cleaned_data['scale_series']
        if series is not None:
            scale = self.cleaned_data['scale']
            if scale != 1:
                raise forms.ValidationError(_('Als een verschalingtijdreeks is opgegeven moet de verschalingsfactor gelijk aan 1 zijn'))
        return series

    def clean_offset_series(self):
        series = self.cleaned_data['offset_series']
        if series is not None:
            offset = self.cleaned_data['offset']
            if offset != 0:
                raise forms.ValidationError(_('Als een compensatietijdreeks is opgegeven moet de compensatiefactor gelijk aan 0 zijn'))
        return series

from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin

class SaveUserMixin:
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

class ContentTypeFilter(admin.SimpleListFilter):
    title = _('Tijdreeks type')
    parameter_name = 'ctid'

    def lookups(self, request, modeladmin):
        ''' Possibilities are: series, formula and manual '''
        ct_types = ContentType.objects.get_for_models(Series,Formula,ManualSeries)
        return [(ct.id, ct.name) for ct in sorted(ct_types.values(), key=lambda x: x.name)]

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(polymorphic_ctype_id = self.value())
        return queryset

class FilterInline(admin.TabularInline):
    from acacia.validation.models import Filter
    model = Filter.series.through
    verbose_name = 'filter'
    verbose_name_plural = 'filters'
    extra = 0
    classes = ('grp-collapse grp-closed',)
    
class ParameterSeriesAdmin(PolymorphicChildModelAdmin):
    actions = [actions.copy_series, actions.download_series, actions.refresh_series, actions.replace_series, actions.series_thumbnails, actions.update_series_properties, actions.empty_series]
    list_filter = ('mlocatie', 'parameter__datasource', 'parameter__datasource__meetlocatie__projectlocatie__project', ContentTypeFilter)
    base_model = Series
    inlines = [FilterInline,]
    #base_form = SeriesForm
    exclude = ('user',)

    raw_id_fields = ('scale_series','offset_series')
    autocomplete_lookup_fields = {
        'fk': ['scale_series', 'offset_series'],
    }
    search_fields = ['name','parameter__name','parameter__datasource__name']

    fieldsets = (
                 (_('Algemeen'), {'fields': ('parameter', 'name', ('unit', 'type'), 'description','timezone'),
                               'classes': ('grp-collapse grp-open',),
                               }),
                 (_('Tijdsinterval'), {'fields': ('from_limit','to_limit'),
                               'classes': ('grp-collapse grp-closed',)
                               }),
                 (_('Bewerkingen'), {'fields': (('resample', 'aggregate',),('scale', 'scale_series'), ('offset','offset_series'), ('cumsum', 'cumstart' ),),
                               'classes': ('grp-collapse grp-closed',),
                              }),
    )

    def save_model(self, request, obj, form, change):
        if obj.parameter:
            obj.mlocatie = obj.parameter.meetlocatie()
        obj.user = request.user
        obj.save()

#class ManualSeriesAdmin(admin.ModelAdmin):
class ManualSeriesAdmin(PolymorphicChildModelAdmin):
    base_model = Series
    actions = [actions.copy_series, actions.series_thumbnails]
    list_display = ('name', 'mlocatie', 'thumbtag', 'unit', 'timezone', 'aantal', 'van', 'tot', 'minimum', 'maximum', 'gemiddelde')
    list_filter = ('mlocatie', 'parameter__datasource', 'parameter__datasource__meetlocatie__projectlocatie__project', ContentTypeFilter)
    exclude = ('parameter','user')
    inlines = [DataPointInline,]
    search_fields = ['name','locatie']
    fieldsets = (
                 (_('Algemeen'), {'fields': ('mlocatie', 'name', ('unit', 'type'), 'description','timezone'),
                               'classes': ('grp-collapse grp-open',),
                               }),
                (_('Tijdsinterval'), {'fields': ('from_limit','to_limit'),
                              'classes': ('grp-collapse grp-closed',)
                              }),
                (_('Bewerkingen'), {'fields': (('resample', 'aggregate',),('scale', 'scale_series'), ('offset','offset_series'), ('cumsum', 'cumstart' ),),
                              'classes': ('grp-collapse grp-closed',),
                            }),
    )

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()
        obj.getproperties().delete() # will be updated in due time

#class FormulaAdmin(SeriesAdmin):
class FormulaSeriesAdmin(PolymorphicChildModelAdmin):
    base_model = Series
    list_filter = ('mlocatie', 'parameter__datasource', 'parameter__datasource__meetlocatie__projectlocatie__project', ContentTypeFilter)
    exclude = ('parameter','user')
    fieldsets = (
                  (_('Algemeen'), {'fields': ('mlocatie', 'name', ('unit', 'type'), 'description','timezone'),
                                'classes': ('grp-collapse grp-open',),
                                }),
                 (_('Tijdsinterval'), {'fields': ('from_limit','to_limit'),
                               'classes': ('grp-collapse grp-closed',)
                               }),
                 (_('Bewerkingen'), {'fields': (('resample', 'aggregate',),('scale', 'scale_series'), ('offset','offset_series'), ('cumsum', 'cumstart' ),),
                               'classes': ('grp-collapse grp-closed',),
                              }),
                 (_('Berekening'), {'fields': ('formula_variables', 'intersect', 'formula_text'),
                               'classes': ('grp-collapse grp-closed',),
                              }),
    )
    filter_horizontal = ('formula_variables',)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()
        obj.getproperties().delete() # will be updated in due time

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
    actions = [actions.create_grid, 
               actions.copy_series, 
               actions.download_series_zip, 
               actions.refresh_series, 
               actions.replace_series, 
               actions.series_thumbnails, 
               actions.update_series_properties, 
               actions.empty_series]
    list_display = ('name', 'thumbtag', 'typename', 'parameter', 'datasource', 'mlocatie', 'timezone', 'unit', 'aantal', 'van', 'tot', 'minimum', 'maximum', 'gemiddelde', 'has_filters')
    base_model = Series
    try:
        from acacia.meetnet.models import Handpeilingen
        from acacia.meetnet.admin import HandpeilingenAdmin
        # allow redirection to meetnet admin
        child_models = ((ManualSeries, ManualSeriesAdmin), (Formula, FormulaSeriesAdmin), (Series, ParameterSeriesAdmin), (Handpeilingen, HandpeilingenAdmin))
    except:
        child_models = ((ManualSeries, ManualSeriesAdmin), (Formula, FormulaSeriesAdmin), (Series, ParameterSeriesAdmin))
        
    exclude = ('user',)

    raw_id_fields = ('scale_series','offset_series')
    autocomplete_lookup_fields = {
        'fk': ['scale_series', 'offset_series'],
    }

    class ContentTypeFilter(admin.SimpleListFilter):
        title = _('Tijdreeks type')
        parameter_name = 'ctid'

        def lookups(self, request, modeladmin):
            ''' Possibilities are: series, formula and manual '''
            models = [Series,Formula,ManualSeries]
            try:
                from acacia.meetnet.models import Handpeilingen
                models.append(Handpeilingen)
            except:
                pass
            ct_types = ContentType.objects.get_for_models(*models)
            return [(ct.id, ct.name) for ct in sorted(ct_types.values(), key=lambda x: x.name)]

        def queryset(self, request, queryset):
            if self.value() is not None:
                return queryset.filter(polymorphic_ctype_id = self.value())
            return queryset


    list_filter = ('mlocatie', 'parameter__datasource', 'parameter__datasource__meetlocatie__projectlocatie__project', ContentTypeFilter)
    search_fields = ['name','parameter__name','parameter__datasource__name']

    base_fieldsets = (
                 (_('Algemeen'), {'fields': ('parameter', 'name', ('unit', 'type'), 'description','timezone'),
                               'classes': ('grp-collapse grp-open',),
                               }),
                 (_('Tijdsinterval'), {'fields': ('from_limit','to_limit'),
                               'classes': ('grp-collapse grp-closed',)
                               }),
                 (_('Bewerkingen'), {'fields': (('resample', 'aggregate',),('scale', 'scale_series'), ('offset','offset_series'), ('cumsum', 'cumstart' ),),
                               'classes': ('grp-collapse grp-closed',),
                              }),
    )

    def save_model(self, request, obj, form, change):
        obj.mlocatie = obj.parameter.meetlocatie()
        obj.user = request.user
        obj.save()


class ChartSeriesInline(admin.StackedInline):
    model = ChartSeries
    raw_id_fields = ('series','series2')
    autocomplete_lookup_fields = {
        'fk': ['series','series2'],
    }
    extra = 0
    fields = (('series', 'order', 'name'), ('axis', 'axislr', 'label'), ('color', 'type', 'series2', 'stack'), ('t0', 't1'), ('y0', 'y1'))
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

class HiLoInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super(HiLoInlineFormSet, self).clean()
        for form in self.forms:
            orient = form.cleaned_data['orientation']
            hi = form.cleaned_data['high']
            lo = form.cleaned_data['low']
            if orient == 'h':
            # horizontal band: low and high must be numebers
                try:
                    van=float(lo)
                    tot=float(hi)
                except:
                    raise forms.ValidationError(_("'van' en 'tot' moeten een getal zijn"))
            else:
                # vertical band: low and high must be datetime
                try:
                    van = dateutil.parser.parse(lo)
                    tot = dateutil.parser.parse(hi)
                except:
                    raise forms.ValidationError(_("'van' en 'tot' moeten een datum zijn"))
            if van > tot:
                raise forms.ValidationError(_("'van' mag niet groter zijn dan 'tot'"))
            
class PlotBandInline(admin.TabularInline):
    model = PlotBand
    classes = ('grp-collapse grp-closed',)
    extra = 0
    formset = HiLoInlineFormSet

class PlotLineInline(admin.TabularInline):
    model = PlotLine
    classes = ('grp-collapse grp-closed',)
    extra = 0
    #formset = HiLoInlineFormSet
    
class ChartAdmin(admin.ModelAdmin):
    actions = [actions.copy_charts,]
    list_display = ('name', 'title', 'tijdreeksen', )
    inlines = [PlotBandInline,PlotLineInline,ChartSeriesInline,]
    exclude = ('user',)
    fieldsets = (
                 ('Algemeen', {'fields': ('name', 'description', 'title'),
                               'classes': ('grp-collapse grp-open',),
                               }),
                 ('Tijdas', {'fields': (('percount', 'perunit',), ('start', 'stop',)),
                               'classes': ('grp-collapse grp-closed',),
                              })
                )

    search_fields = ['name','description', 'title']
    formfield_overrides = {models.TextField: {'widget': forms.Textarea(attrs={'class': 'htmleditor'})}}

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
            raise forms.ValidationError(_('{0} is een ongeldige python variable').format(name))
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


from actions import update_kental
class KeyFigureAdmin(admin.ModelAdmin):
    actions = [update_kental]
    model = KeyFigure
    exclude = ('value', )
    filter_horizontal = ('variables',)
    list_filter = ('locatie', )
    list_display = ('name','locatie', 'value', 'last_update')

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
admin.site.register(CalibrationData, CalibrationAdmin)
admin.site.register(KeyFigure, KeyFigureAdmin)

admin.site.register(PlotBand)
admin.site.register(PlotLine)
admin.site.register(LineStyle)
admin.site.register(BandStyle)
