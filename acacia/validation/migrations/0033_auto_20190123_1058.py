# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-01-23 09:58
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('validation', '0032_auto_20181114_0750'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ruleorder',
            options={'ordering': ['order'], 'verbose_name': 'Validatieregels'},
        ),
    ]
