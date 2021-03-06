# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def copy_locaties(apps,schema_editor):
    Datasource = apps.get_model('data', 'Datasource')
    for ds in Datasource.objects.all():
        ds.locations.add(ds.meetlocatie)
    
class Migration(migrations.Migration):

    dependencies = [
        ('data', '0007_auto_20160928_1107'),
    ]

    operations = [
        migrations.RunPython(copy_locaties),
    ]
