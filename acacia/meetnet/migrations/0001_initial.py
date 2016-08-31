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
            name='Channel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.IntegerField()),
                ('identification', models.CharField(max_length=20)),
                ('reference_level', models.FloatField()),
                ('reference_unit', models.CharField(max_length=10)),
                ('range', models.FloatField()),
                ('range_unit', models.CharField(max_length=10)),
            ],
            options={
                'verbose_name': 'Kanaal',
                'verbose_name_plural': 'Kanalen',
            },
        ),
        migrations.CreateModel(
            name='Datalogger',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('serial', models.CharField(unique=True, max_length=50, verbose_name=b'serienummer')),
                ('model', models.CharField(default=b'14', max_length=50, verbose_name=b'type', choices=[(b'micro', b'Micro-Diver'), (b'3', b'TD-Diver'), (b'ctd', b'CTD-Diver'), (b'16', b'Cera-Diver'), (b'14', b'Mini-Diver'), (b'baro', b'Baro-Diver')])),
            ],
            options={
                'ordering': ['serial'],
            },
        ),
        migrations.CreateModel(
            name='LoggerDatasource',
            fields=[
                ('datasource_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='data.Datasource')),
                ('logger', models.ForeignKey(related_name='datasources', to='meetnet.Datalogger')),
            ],
            options={
                'verbose_name': 'Loggerdata',
                'verbose_name_plural': 'Loggerdata',
            },
            bases=('data.datasource',),
        ),
        migrations.CreateModel(
            name='LoggerPos',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateTimeField(help_text=b'Tijdstip van start datalogger', verbose_name=b'start')),
                ('end_date', models.DateTimeField(help_text=b'Tijdstrip van stoppen datalogger', null=True, verbose_name=b'stop', blank=True)),
                ('refpnt', models.FloatField(help_text=b'ophangpunt in meter tov NAP', null=True, verbose_name=b'referentiepunt', blank=True)),
                ('depth', models.FloatField(help_text=b'lengte van ophangkabel in meter', null=True, verbose_name=b'kabellengte', blank=True)),
                ('remarks', models.TextField(verbose_name=b'opmerkingen', blank=True)),
                ('baro', models.ForeignKey(blank=True, to='data.Series', help_text=b'tijdreeks voor luchtdruk compensatie', null=True, verbose_name=b'luchtdruk')),
                ('logger', models.ForeignKey(to='meetnet.Datalogger')),
            ],
            options={
                'ordering': ['logger', 'start_date'],
                'verbose_name': 'DataloggerInstallatie',
            },
        ),
        migrations.CreateModel(
            name='MonFile',
            fields=[
                ('sourcefile_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='data.SourceFile')),
                ('company', models.CharField(max_length=50)),
                ('compstat', models.CharField(max_length=10)),
                ('date', models.DateTimeField()),
                ('monfilename', models.CharField(max_length=512, verbose_name=b'Filename')),
                ('createdby', models.CharField(max_length=100)),
                ('instrument_type', models.CharField(max_length=50)),
                ('status', models.CharField(max_length=50)),
                ('serial_number', models.CharField(max_length=50)),
                ('instrument_number', models.CharField(max_length=50)),
                ('location', models.CharField(max_length=50)),
                ('sample_period', models.CharField(max_length=50)),
                ('sample_method', models.CharField(max_length=10)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('num_channels', models.IntegerField(default=1)),
                ('num_points', models.IntegerField()),
                ('source', models.ForeignKey(verbose_name=b'diver', blank=True, to='meetnet.LoggerPos', null=True)),
            ],
            bases=('data.sourcefile',),
        ),
        migrations.CreateModel(
            name='Network',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50, verbose_name=b'naam')),
                ('logo', models.ImageField(upload_to=b'logos')),
                ('homepage', models.URLField(help_text=b'website van meetnetbeheerder', blank=True)),
                ('bound', models.URLField(help_text=b'url van kml file met begrenzing van het meetnet', verbose_name=b'grens', blank=True)),
                ('last_round', models.DateField(null=True, verbose_name=b'laatste uitleesronde', blank=True)),
                ('next_round', models.DateField(null=True, verbose_name=b'volgende uitleesronde', blank=True)),
            ],
            options={
                'verbose_name': 'netwerk',
                'verbose_name_plural': 'netwerken',
            },
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('photo', models.ImageField(upload_to=b'fotos')),
            ],
            options={
                'verbose_name': 'foto',
                'verbose_name_plural': "foto's",
            },
        ),
        migrations.CreateModel(
            name='Screen',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nr', models.IntegerField(default=1, verbose_name=b'filternummer')),
                ('density', models.FloatField(default=1000.0, help_text=b'dichtheid van het water in de peilbuis in kg/m3', verbose_name=b'dichtheid')),
                ('refpnt', models.FloatField(help_text=b'bovenkant peilbuis in meter tov NAP', null=True, verbose_name=b'bovenkant buis', blank=True)),
                ('top', models.FloatField(help_text=b'bovenkant filter in meter min maaiveld', null=True, verbose_name=b'bovenkant filter', blank=True)),
                ('bottom', models.FloatField(help_text=b'onderkant filter in meter min maaiveld', null=True, verbose_name=b'onderkant filter', blank=True)),
                ('diameter', models.FloatField(default=32, help_text=b'diameter in mm (standaard = 32 mm)', null=True, verbose_name=b'diameter buis', blank=True)),
                ('material', models.CharField(default=b'pvc', max_length=10, verbose_name=b'materiaal', blank=True, choices=[(b'pvc', b'PVC'), (b'hdpe', b'HDPE'), (b'ss', b'RVS'), (b'ms', b'Staal')])),
                ('chart', models.ImageField(upload_to=b'charts', null=True, verbose_name=b'grafiek', blank=True)),
            ],
            options={
                'ordering': ['well', 'nr'],
                'verbose_name': 'filter',
                'verbose_name_plural': 'filters',
            },
        ),
        migrations.CreateModel(
            name='Well',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50, verbose_name=b'naam')),
                ('nitg', models.CharField(max_length=50, verbose_name=b'TNO/NITG nummer', blank=True)),
                ('bro', models.CharField(max_length=50, verbose_name=b'BRO nummer', blank=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(help_text=b'locatie in rijksdriehoeksstelsel coordinaten', srid=28992, verbose_name=b'locatie')),
                ('description', models.TextField(verbose_name=b'locatieomschrijving', blank=True)),
                ('maaiveld', models.FloatField(help_text=b'maaiveld in meter tov NAP', null=True, verbose_name=b'maaiveld', blank=True)),
                ('date', models.DateField(null=True, verbose_name=b'constructiedatum', blank=True)),
                ('straat', models.CharField(max_length=60, blank=True)),
                ('huisnummer', models.CharField(max_length=6, blank=True)),
                ('postcode', models.CharField(max_length=8, blank=True)),
                ('plaats', models.CharField(max_length=60, blank=True)),
                ('log', models.ImageField(upload_to=b'logs', null=True, verbose_name=b'boorstaat', blank=True)),
                ('chart', models.ImageField(upload_to=b'charts', null=True, verbose_name=b'grafiek', blank=True)),
                ('g', models.FloatField(default=9.80665, help_text=b'valversnelling in m/s2', verbose_name=b'valversnelling')),
                ('network', models.ForeignKey(verbose_name=b'Meetnet', to='meetnet.Network')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'put',
                'verbose_name_plural': 'putten',
            },
        ),
        migrations.AddField(
            model_name='screen',
            name='well',
            field=models.ForeignKey(verbose_name=b'put', to='meetnet.Well'),
        ),
        migrations.AddField(
            model_name='photo',
            name='well',
            field=models.ForeignKey(to='meetnet.Well'),
        ),
        migrations.AddField(
            model_name='loggerpos',
            name='screen',
            field=models.ForeignKey(verbose_name=b'filter', blank=True, to='meetnet.Screen', null=True),
        ),
        migrations.AddField(
            model_name='channel',
            name='monfile',
            field=models.ForeignKey(to='meetnet.MonFile'),
        ),
        migrations.AlterUniqueTogether(
            name='screen',
            unique_together=set([('well', 'nr')]),
        ),
    ]
