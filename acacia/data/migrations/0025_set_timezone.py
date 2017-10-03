# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.utils.timezone import get_current_timezone

def settz(apps, schema_editor):
    model = apps.get_model('data', 'Datasource')
    for m in model.objects.all():
        if not m.timezone:
            m.timezone = get_current_timezone() 
            m.save()
    model = apps.get_model('data', 'Series')
    for m in model.objects.all():
        if not m.timezone:
            try:
                m.timezone = m.parameter.datasource.timezone
            except:
                m.timezone = get_current_timezone()
            m.save()
    model = apps.get_model('data', 'Chart')
    for m in model.objects.all():
        if not m.timezone:
            m.timezone = get_current_timezone() 
            m.save()
            
class Migration(migrations.Migration):

    dependencies = [
        ('data', '0024_auto_20170918_0927'),
    ]

    operations = [
        migrations.RunPython(settz),
    ]
