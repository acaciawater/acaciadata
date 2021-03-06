# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-22 10:16
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meetnet', '0024_auto_20171218_2254'),
    ]

    operations = [
        migrations.AddField(
            model_name='screen',
            name='aquifer',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='aquifer'),
        ),
        migrations.AddField(
            model_name='well',
            name='owner',
            field=models.CharField(blank=True, max_length=40, null=True, verbose_name='owner'),
        ),
        migrations.AlterField(
            model_name='well',
            name='bro',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='BRO id'),
        ),
        migrations.AlterField(
            model_name='well',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='well',
            name='huisnummer',
            field=models.CharField(blank=True, max_length=12, null=True, verbose_name='house number'),
        ),
        migrations.AlterField(
            model_name='well',
            name='nitg',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='TNO/NITG identification'),
        ),
        migrations.AlterField(
            model_name='well',
            name='plaats',
            field=models.CharField(blank=True, max_length=60, null=True, verbose_name='locality'),
        ),
        migrations.AlterField(
            model_name='well',
            name='postcode',
            field=models.CharField(blank=True, max_length=8, null=True, verbose_name='postal code'),
        ),
        migrations.AlterField(
            model_name='well',
            name='straat',
            field=models.CharField(blank=True, max_length=60, null=True, verbose_name='street name'),
        ),
    ]
