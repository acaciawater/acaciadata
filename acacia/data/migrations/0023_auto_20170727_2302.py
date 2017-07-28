# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0022_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datasource',
            name='timezone',
            field=models.CharField(default=b'Africa/Kampala', max_length=50, verbose_name=b'Tijzone', blank=True),
        ),
        migrations.AlterField(
            model_name='meetlocatie',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(help_text=b'Meetlocatie in geografische coordinaten', srid=4326, verbose_name=b'locatie'),
        ),
        migrations.AlterField(
            model_name='projectlocatie',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(help_text=b'Projectlocatie in geografische coordinaten', srid=4326, verbose_name=b'locatie'),
        ),
    ]
