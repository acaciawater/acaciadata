# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.contrib.contenttypes.models import ContentType

def fixct(apps, schema_editor):
    #all polymorphic items
    for name in ['Series', 'Chart','Formula', 'ManualSeries', 'Grid']:
        model = apps.get_model('data', name)
        ct = ContentType.objects.get_for_model(model)
        for f in model.objects.all():
            f.polymorphic_ctype_id = ct.id
            f.save()
            
class Migration(migrations.Migration):

    dependencies = [
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(fixct),
    ]
