from django.contrib import admin, messages
from acacia.validation.models import Validation, Result,\
    BaseRule, ValueRule, SeriesRule, NoDataRule, OutlierRule, DiffRule,\
    ScriptRule, SlotRule, SubResult, RuleOrder, RollingRule, RangeRule
from acacia.validation.views import download
from polymorphic.admin.parentadmin import PolymorphicParentModelAdmin
from polymorphic.admin.childadmin import PolymorphicChildModelAdmin
from polymorphic.admin.filters import PolymorphicChildModelFilter
from django.shortcuts import redirect

def test_validation(modeladmin, request, queryset):
    count = queryset.count()
    for v in queryset:
        v.validpoint_set.all().delete()
        result = v.persist()
    messages.success(request, '{} validaties uitgevoerd'.format(count))

def download_validation(modeladmin, request, queryset):
    for v in queryset:
        download(request, pk = v.pk)
        
test_validation.short_description='Valideren'

@admin.register(BaseRule)
class BaseRuleAdmin(PolymorphicParentModelAdmin):
    base_model = BaseRule
    child_models = (ValueRule, SeriesRule, NoDataRule, OutlierRule, DiffRule, ScriptRule, SlotRule, RollingRule, RangeRule)
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
    actions = [test_validation,download_validation]
    inlines = [RuleInline]
    exclude = ('users','validated','valid')
    #filter_horizontal = ('users',)
    list_filter = ('series','last_validation','valid',RuleFilter)
    list_display = ('series','last_validation','valid','rule_names')
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

