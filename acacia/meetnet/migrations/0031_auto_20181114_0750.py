# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-11-14 06:50
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meetnet', '0030_auto_20180105_0128'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='well',
            options={'ordering': ['nitg', 'name'], 'verbose_name': 'well', 'verbose_name_plural': 'wells'},
        ),
    ]
