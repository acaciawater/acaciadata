# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-18 22:09
from __future__ import unicode_literals

from django.db import migrations
from acacia.data.util import setWGS84

def reproject_all(apps, schema_editor):
    model = apps.get_model('meetnet', 'Well')
    for obj in model.objects.all():
        setWGS84(obj)

class Migration(migrations.Migration):

    dependencies = [
        ('meetnet', '0024_auto_20171218_2254'),
    ]

    operations = [
        migrations.RunPython(reproject_all),
    ]