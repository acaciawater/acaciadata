# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-19 21:51
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0030_auto_20171215_0155'),
    ]

    operations = [
        migrations.AddField(
            model_name='meetlocatie',
            name='wgs',
            field=django.contrib.gis.db.models.fields.PointField(help_text='Location in longitude/latitude coordinates', null=True, srid=4326, verbose_name='location'),
        ),
        migrations.AddField(
            model_name='projectlocatie',
            name='wgs',
            field=django.contrib.gis.db.models.fields.PointField(help_text='Location in longitude/latitude coordinates', null=True, srid=4326, verbose_name='location'),
        ),
        migrations.AlterField(
            model_name='meetlocatie',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(help_text='Location in longitude/latitude coordinates', srid=28992, verbose_name='location'),
        ),
        migrations.AlterField(
            model_name='projectlocatie',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(help_text='Location in longitude/latitude coordinates', srid=28992, verbose_name='location'),
        ),
    ]