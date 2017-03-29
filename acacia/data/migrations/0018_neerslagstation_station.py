# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0017_auto_20170213_2239'),
    ]

    operations = [
        migrations.CreateModel(
            name='NeerslagStation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nummer', models.IntegerField()),
                ('naam', models.CharField(max_length=50)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=28992)),
            ],
            options={
                'ordering': ('naam',),
            },
        ),
        migrations.CreateModel(
            name='Station',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nummer', models.IntegerField()),
                ('naam', models.CharField(max_length=50)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=28992)),
            ],
            options={
                'ordering': ('naam',),
            },
        ),
    ]
