# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-28 00:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0037_merge_20171228_0127'),
        ('meetnet', '0025_auto_20171222_1116'),
    ]

    operations = [
        migrations.AddField(
            model_name='screen',
            name='logger_levels',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='waterlevel', to='data.Series', verbose_name='water level'),
        ),
        migrations.AddField(
            model_name='screen',
            name='manual_levels',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='manual', to='data.Series', verbose_name='manual measurements'),
        ),
    ]