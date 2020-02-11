from django.contrib import admin, messages
from acacia.validation.models import Validation, Result,\
    BaseRule, ValueRule, SeriesRule, NoDataRule, OutlierRule, DiffRule,\
    ScriptRule, SlotRule, SubResult, RuleOrder, RollingRule, RangeRule, Filter,\
    FilterOrder, MaaiveldRule
from polymorphic.admin.parentadmin import PolymorphicParentModelAdmin
from polymorphic.admin.childadmin import PolymorphicChildModelAdmin
from polymorphic.admin.filters import PolymorphicChildModelFilter
from django.shortcuts import redirect
from django.conf import settings

def validate(modeladmin, request, queryset):
    count = queryset.count()
    for v in queryset:
        v.reset()
        v.persist()
    messages.success(request, '{} validaties uitgevoerd'.format(count))
validate.short_description='Valideren'

def validate_and_accept(modeladmin, request, queryset):
    count = queryset.count()
    for v in queryset:
        v.apply_and_accept(request.user)
    messages.success(request, '{} validaties uitgevoerd'.format(count))
validate_and_accept.short_description='Valideren en accepteren'

def accept(modeladmin, request, queryset):
    count = queryset.count()
    for v in queryset:
        v.accept(request.user)
    messages.success(request, '{} validaties geaccepteerd'.format(count))
accept.short_description='Accepteren'

def apply_filter(modeladmin, request, queryset):
    count = queryset.count()
    for filt in queryset:
        for series in filt.series.all():
            filtered_data = filt.apply(series.to_pandas(),context={})
            series.replace(filtered_data)
    messages.success(request, '{} filters toegepast'.format(count))
apply_filter.short_description='Geselecteerde filters toepassen op betreffende tijdreeksen'

@admin.register(BaseRule)
class BaseRuleAdmin(PolymorphicParentModelAdmin):
    base_model = BaseRule
    child_models = (ValueRule, SeriesRule, NoDataRule, OutlierRule, DiffRule, ScriptRule, SlotRule, RollingRule, RangeRule, MaaiveldRule)
    list_filter = (PolymorphicChildModelFilter,)
    search_fields = ('name','description')

@admin.register(ValueRule)
class ValueRuleAdmin(PolymorphicChildModelAdmin):
    base_model = ValueRule

@admin.register(SeriesRule)
class SeriesRuleAdmin(PolymorphicChildModelAdmin):
    base_model = SeriesRule
    raw_id_fields = ['series']
    autocomplete_lookup_fields = {
        'fk': ['series'],
    }

@admin.register(NoDataRule)
class NoDataRuleAdmin(PolymorphicChildModelAdmin):
    base_model = NoDataRule
    
@admin.register(OutlierRule)
class OutlierRuleAdmin(NoDataRuleAdmin):
    base_model = OutlierRule
    
@admin.register(DiffRule)
class DiffRuleAdmin(NoDataRuleAdmin):
    base_model = DiffRule

@admin.register(ScriptRule)
class ScriptRuleAdmin(NoDataRuleAdmin):
    base_model = ScriptRule

@admin.register(SlotRule)
class SlotRuleAdmin(NoDataRuleAdmin):
    base_model = SlotRule
    exclude=('comp',)

@admin.register(RollingRule)
class RollingRuleAdmin(NoDataRuleAdmin):
    base_model = RollingRule

@admin.register(RangeRule)
class RangeRuleAdmin(NoDataRuleAdmin):
    base_model = RangeRule
    exclude = ('comp',)
    
class RuleInline(admin.TabularInline):
    model = RuleOrder
    extra = 1

class RuleFilter(admin.SimpleListFilter):
    title = 'Regel'
    parameter_name = 'rule'

    def lookups(self, request, modeladmin):

        return [(r.id, r.name) for r in BaseRule.objects.all()]

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(rules__id = self.value())
        return queryset
        
@admin.register(Validation)
class ValidationAdmin(admin.ModelAdmin):
    actions = [validate,accept,validate_and_accept]
    inlines = [RuleInline]
    exclude = ('users','validated','valid')
    #filter_horizontal = ('users',)
    list_filter = ('series','last_validation','valid',RuleFilter)
    list_display = ('series','last_validation','valid','num_invalid_points','rule_names')
    raw_id_fields = ['series']
    autocomplete_lookup_fields = {
        'fk': ['series'],
    }
    def response_add(self, request, obj, post_url_continue=None):
        ret = admin.ModelAdmin.response_add(self, request, obj, post_url_continue=post_url_continue)
        if 'next' in request.GET:
            return redirect(request.GET['next'])
        else:
            return ret
        
    def response_change(self, request, obj):
        ret = admin.ModelAdmin.response_change(self, request, obj)
        if 'next' in request.GET:
            return redirect(request.GET['next'])
        else:
            return ret
    
@admin.register(SubResult)
class SubResultAdmin(admin.ModelAdmin):
    list_display = ('rule', 'validation', 'valid', 'invalid', 'first_invalid')
    list_filter = ('validation', 'rule')

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('validation', 'xlfile', 'begin','end', 'user','date',)
    list_filter = ('validation__series__mlocatie', 'date', 'user',)

@admin.register(FilterOrder)
class FilterOrderAdmin(admin.ModelAdmin):
    pass

class FilterInline(admin.TabularInline):
    model = FilterOrder
    extra = 1

@admin.register(Filter)
class FilterAdmin(admin.ModelAdmin):
    inlines = [FilterInline]
    actions = [apply_filter,]
#     raw_id_fields = ['series']
#     autocomplete_lookup_fields = {
#         'm2m': ['series'],
#     }
    filter_horizontal = ('series',)
    
    
try:
    @admin.register(MaaiveldRule)
    class MaaiveldRuleAdmin(admin.ModelAdmin):
        model = MaaiveldRule
except:
    pass