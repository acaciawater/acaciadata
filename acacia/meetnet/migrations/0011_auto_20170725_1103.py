# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

def baro2meteo(apps, schema_editor):
    """ copy well.baro to well.meteo """
    Well = apps.get_model('meetnet', 'Well')
    Meteo = apps.get_model('meetnet', 'MeteoData')
    for w in Well.objects.all():
        Meteo.objects.get_or_create(well=w,defaults={'baro':w.baro}) 

class Migration(migrations.Migration):

    dependencies = [
        ('meetnet', '0010_auto_20170725_1103'),
    ]

    operations = [
        migrations.RunPython(baro2meteo)
    ]
