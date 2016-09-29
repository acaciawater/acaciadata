# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0005_auto_20160831_2337'),
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
        migrations.AddField(
            model_name='datasource',
            name='locations',
            field=models.ManyToManyField(help_text=b'Meetlocaties voor deze gegevensbron', related_name='datasources', to='data.MeetLocatie'),
        ),
        migrations.AlterField(
            model_name='datasource',
            name='meetlocatie',
            field=models.ForeignKey(help_text=b'Meetlocatie van deze gegevensbron', to='data.MeetLocatie'),
        ),
        migrations.AlterField(
            model_name='datasource',
            name='url',
            field=models.CharField(help_text=b'volledige url van de gegevensbron. Leeg laten voor handmatige uploads of default url van generator', max_length=200, null=True, blank=True),
        ),
    ]
