'''
Created on Nov 16, 2015

@author: stephane
'''
from django.contrib import admin

# Register your models here.
from acacia.data.admin import DatasourceAdmin, ChartSeriesInline, DatasourceForm
from acacia.gwsforecast.models import GWSForecast
from django.contrib.admin.options import ModelAdmin


class GWSForecastForm(DatasourceForm):
    model = GWSForecast

class GWSAdmin(DatasourceAdmin):
    form = GWSForecastForm
    fieldsets = (
                 ('Algemeen', {'fields': ('name', 'description', 'timezone', 'meetlocatie', 'hist_gws','hist_ev','hist_pt','forec_et','forec_pt','forec_tmp' ),
                               'classes': ('grp-collapse grp-open',),
                               }),
                 ('Bronnen', {'fields': (('generator', 'autoupdate'), 'url',('username', 'password',), 'config',),
                               'classes': ('grp-collapse grp-closed',),
                              }),
    )

admin.site.register(GWSForecast, GWSAdmin)
