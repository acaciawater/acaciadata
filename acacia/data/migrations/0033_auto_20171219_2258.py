# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-19 21:58
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0032_auto_20171219_2252'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='meetlocatie',
            name='location',
        ),
        migrations.RemoveField(
            model_name='projectlocatie',
            name='location',
        ),
    ]
