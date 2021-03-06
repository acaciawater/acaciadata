# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-27 08:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meetnet', '0019_auto_20171025_0051'),
    ]

    operations = [
        migrations.AddField(
            model_name='screen',
            name='depth',
            field=models.FloatField(blank=True, help_text=b'diepte peilbuis in meter min maaiveld', null=True, verbose_name=b'diepte peilbuis'),
        ),
        migrations.AlterField(
            model_name='loggerpos',
            name='end_date',
            field=models.DateTimeField(blank=True, help_text=b'Tijdstip van stoppen datalogger', null=True, verbose_name=b'stop'),
        ),
    ]
