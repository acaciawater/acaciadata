# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0003_auto_20160311_2029'),
    ]

    operations = [
        migrations.CreateModel(
            name='CalibrationData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sensor_value', models.FloatField(verbose_name=b'meetwaarde')),
                ('calib_value', models.FloatField(verbose_name=b'ijkwaarde')),
                ('datasource', models.ForeignKey(to='data.Datasource')),
                ('parameter', models.ForeignKey(to='data.Parameter')),
            ],
            options={
                'verbose_name': 'IJkpunt',
                'verbose_name_plural': 'IJkset',
            },
        ),
        migrations.CreateModel(
            name='KeyFigure',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name=b'naam')),
                ('description', models.TextField(null=True, verbose_name=b'omschrijving', blank=True)),
                ('formula', models.TextField(null=True, verbose_name=b'berekening', blank=True)),
                ('last_update', models.DateTimeField(auto_now=True, verbose_name=b'bijgewerkt')),
                ('startDate', models.DateField(null=True, blank=True)),
                ('stopDate', models.DateField(null=True, blank=True)),
                ('value', models.FloatField(null=True, verbose_name=b'waarde', blank=True)),
                ('locatie', models.ForeignKey(to='data.MeetLocatie')),
                ('variables', smart_selects.db_fields.ChainedManyToManyField(chained_model_field=b'locatie', to='data.Variable', verbose_name=b'variabelen', chained_field=models.ForeignKey(to='data.MeetLocatie'))),
            ],
            options={
                'verbose_name': 'Kental',
                'verbose_name_plural': 'Kentallen',
            },
        ),
        migrations.AlterUniqueTogether(
            name='keyfigure',
            unique_together=set([('locatie', 'name')]),
        ),
    ]
