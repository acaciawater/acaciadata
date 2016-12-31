from django.contrib import admin
from acacia.validation.models import Validation, Result,\
    BaseRule, ValueRule, SeriesRule, NoDataRule, OutlierRule, DiffRule
from acacia.validation.views import download
from polymorphic.admin.parentadmin import PolymorphicParentModelAdmin
from polymorphic.admin.childadmin import PolymorphicChildModelAdmin
from polymorphic.admin.filters import PolymorphicChildModelFilter

def test_validation(modeladmin, request, queryset):
    for v in queryset:
        result = v.persist()

def download_validation(modeladmin, request, queryset):
    for v in queryset:
        download(request, pk = v.pk)
        
test_validation.short_description='Valideren'

@admin.register(BaseRule)
class BaseRuleAdmin(PolymorphicParentModelAdmin):
    base_model = BaseRule
    child_models = (ValueRule, SeriesRule, NoDataRule, OutlierRule, DiffRule)
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
    
# class RuleAdmin(admin.ModelAdmin):
#     raw_id_fields = ['series']
#     autocomplete_lookup_fields = {
#         'fk': ['series'],
#     }
#     
class ValidationAdmin(admin.ModelAdmin):
    actions = [test_validation,download_validation]
    list_filter = ('series',)
    filter_horizontal = ('rules',)
    raw_id_fields = ['series']
    autocomplete_lookup_fields = {
        'fk': ['series'],
    }
    
class ResultAdmin(admin.ModelAdmin):
    list_display = ('validation', 'begin','end', 'user',)
    list_filter = ('validation__series', 'begin', 'end', 'user',)

#admin.site.register(Rule,RuleAdmin)
admin.site.register(Validation,ValidationAdmin)
admin.site.register(Result,ResultAdmin)