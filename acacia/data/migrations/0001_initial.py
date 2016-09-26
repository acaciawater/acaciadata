# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import acacia.data.upload
import django.contrib.auth.models
import django.contrib.gis.db.models.fields
from django.conf import settings
import acacia.data.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Chart',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name=b'naam')),
                ('description', models.TextField(help_text=b'Toelichting bij grafiek op het dashboard', null=True, verbose_name=b'toelichting', blank=True)),
                ('title', models.CharField(max_length=50, verbose_name=b'titel')),
                ('start', models.DateTimeField(null=True, blank=True)),
                ('stop', models.DateTimeField(null=True, blank=True)),
                ('percount', models.IntegerField(default=2, help_text=b'maximaal aantal periodes terug in de tijd (0 = alle perioden)', verbose_name=b'aantal perioden')),
                ('perunit', models.CharField(default=b'months', max_length=10, verbose_name=b'periodelengte', choices=[(b'hours', b'uur'), (b'days', b'dag'), (b'weeks', b'week'), (b'months', b'maand'), (b'years', b'jaar')])),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Grafiek',
                'verbose_name_plural': 'Grafieken',
            },
        ),
        migrations.CreateModel(
            name='ChartSeries',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField(default=1, verbose_name=b'volgorde')),
                ('name', models.CharField(max_length=50, null=True, verbose_name=b'legendanaam', blank=True)),
                ('axis', models.IntegerField(default=1, verbose_name=b'Nummer y-as')),
                ('axislr', models.CharField(default=b'l', max_length=2, verbose_name=b'Positie y-as', choices=[(b'l', b'links'), (b'r', b'rechts')])),
                ('color', models.CharField(help_text=b'Standaard kleur (bv Orange) of rgba waarde (bv rgba(128,128,0,1)) of hexadecimaal getal (bv #ffa500)', max_length=20, null=True, verbose_name=b'Kleur', blank=True)),
                ('type', models.CharField(default=b'line', max_length=10, choices=[(b'line', b'lijn'), (b'column', b'staaf'), (b'scatter', b'punt'), (b'area', b'area'), (b'spline', b'spline')])),
                ('stack', models.CharField(help_text=b'leeg laten of <i>normal</i> of <i>percent</i>', max_length=20, null=True, verbose_name=b'stapel', blank=True)),
                ('label', models.CharField(default=b'', max_length=20, null=True, help_text=b'label op de y-as', blank=True)),
                ('y0', models.FloatField(null=True, verbose_name=b'ymin', blank=True)),
                ('y1', models.FloatField(null=True, verbose_name=b'ymax', blank=True)),
                ('t0', models.DateTimeField(null=True, verbose_name=b'start', blank=True)),
                ('t1', models.DateTimeField(null=True, verbose_name=b'stop', blank=True)),
            ],
            options={
                'ordering': ['order', 'name'],
                'verbose_name': 'tijdreeks',
                'verbose_name_plural': 'tijdreeksen',
            },
        ),
        migrations.CreateModel(
            name='Dashboard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name=b'naam')),
                ('description', models.TextField(null=True, verbose_name=b'omschrijving', blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='DashboardChart',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField(default=1, verbose_name=b'volgorde')),
            ],
            options={
                'ordering': ['order'],
                'verbose_name': 'Grafiek',
                'verbose_name_plural': 'Grafieken',
            },
        ),
        migrations.CreateModel(
            name='DataPoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(verbose_name=b'Tijdstip')),
                ('value', models.FloatField(verbose_name=b'Waarde')),
            ],
            options={
                'verbose_name': 'Meetwaarde',
                'verbose_name_plural': 'Meetwaarden',
            },
        ),
        migrations.CreateModel(
            name='Datasource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name=b'naam')),
                ('description', models.TextField(null=True, verbose_name=b'omschrijving', blank=True)),
                ('url', models.CharField(help_text=b'volledige url van de gegevensbron. Leeg laten voor handmatige uploads', max_length=200, null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name=b'Aangemaakt op')),
                ('last_download', models.DateTimeField(null=True, verbose_name=b'geactualiseerd', blank=True)),
                ('autoupdate', models.BooleanField(default=True)),
                ('config', models.TextField(default=b'{}', help_text=b'Geldige JSON dictionary', null=True, verbose_name=b'Additionele configuraties', blank=True)),
                ('username', models.CharField(default=b'anonymous', max_length=50, blank=True, help_text=b'Gebruikersnaam voor downloads', null=True, verbose_name=b'Gebuikersnaam')),
                ('password', models.CharField(help_text=b'Wachtwoord voor downloads', max_length=50, null=True, verbose_name=b'Wachtwoord', blank=True)),
                ('timezone', models.CharField(default=b'Europe/Amsterdam', max_length=50, verbose_name=b'Tijzone', blank=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'gegevensbron',
                'verbose_name_plural': 'gegevensbronnen',
            },
            bases=(models.Model, acacia.data.models.LoggerSourceMixin),
        ),
        migrations.CreateModel(
            name='Generator',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50, verbose_name=b'naam')),
                ('classname', models.CharField(help_text=b'volledige naam van de generator klasse, bijvoorbeeld acacia.data.generators.knmi.Meteo', max_length=50, verbose_name=b'python klasse')),
                ('description', models.TextField(null=True, verbose_name=b'omschrijving', blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='MeetLocatie',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name=b'naam')),
                ('description', models.TextField(null=True, verbose_name=b'omschrijving', blank=True)),
                ('image', models.ImageField(null=True, upload_to=acacia.data.upload.meetlocatie_upload, blank=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(help_text=b'Meetlocatie in Rijksdriehoekstelsel coordinaten', srid=28992, verbose_name=b'locatie')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
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
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=254, blank=True)),
                ('subject', models.TextField(default=b'acaciadata.com update rapport', blank=True)),
                ('level', models.CharField(default=b'ERROR', help_text=b'Niveau van berichtgeving', max_length=10, verbose_name=b'Niveau', choices=[(b'DEBUG', b'Debug'), (b'INFO', b'Informatie'), (b'WARNING', b'Waarschuwingen'), (b'ERROR', b'Fouten')])),
                ('active', models.BooleanField(default=True, verbose_name=b'activeren')),
                ('datasource', models.ForeignKey(help_text=b'Gegevensbron welke gevolgd wordt', to='data.Datasource')),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, help_text=b'Gebruiker die berichtgeving ontvangt over updates', null=True, verbose_name=b'Gebruiker')),
            ],
            options={
                'verbose_name': 'Email berichten',
                'verbose_name_plural': 'Email berichten',
            },
        ),
        migrations.CreateModel(
            name='Parameter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name=b'naam')),
                ('description', models.TextField(null=True, verbose_name=b'omschrijving', blank=True)),
                ('unit', models.CharField(default=b'm', max_length=10, verbose_name=b'eenheid')),
                ('type', models.CharField(default=b'line', max_length=20, choices=[(b'line', b'lijn'), (b'column', b'staaf'), (b'scatter', b'punt'), (b'area', b'area'), (b'spline', b'spline')])),
                ('thumbnail', models.ImageField(max_length=200, null=True, upload_to=acacia.data.upload.param_thumb_upload, blank=True)),
                ('datasource', models.ForeignKey(to='data.Datasource')),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model, acacia.data.models.LoggerSourceMixin),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50)),
                ('description', models.TextField(null=True, verbose_name=b'omschrijving', blank=True)),
                ('image', models.ImageField(null=True, upload_to=acacia.data.upload.project_upload, blank=True)),
                ('logo', models.ImageField(null=True, upload_to=acacia.data.upload.project_upload, blank=True)),
                ('theme', models.CharField(default=b'dark-blue', help_text=b'Thema voor grafieken', max_length=50, verbose_name=b'thema', choices=[(b'dark-blue', b'blauw'), (b'darkgreen', b'groen'), (b'gray', b'grijs'), (b'grid', b'grid'), (b'skies', b'wolken')])),
            ],
            options={
                'verbose_name_plural': 'projecten',
            },
        ),
        migrations.CreateModel(
            name='ProjectLocatie',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name=b'naam')),
                ('description', models.TextField(null=True, verbose_name=b'omschrijving', blank=True)),
                ('image', models.ImageField(null=True, upload_to=acacia.data.upload.locatie_upload, blank=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(help_text=b'Projectlocatie in Rijksdriehoekstelsel coordinaten', srid=28992, verbose_name=b'locatie')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Series',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name=b'naam')),
                ('description', models.TextField(null=True, verbose_name=b'omschrijving', blank=True)),
                ('unit', models.CharField(max_length=10, null=True, verbose_name=b'eenheid', blank=True)),
                ('type', models.CharField(default=b'line', choices=[(b'line', b'lijn'), (b'column', b'staaf'), (b'scatter', b'punt'), (b'area', b'area'), (b'spline', b'spline')], max_length=20, blank=True, help_text=b'Standaard weeggave op grafieken', verbose_name=b'weergave')),
                ('thumbnail', models.ImageField(max_length=200, null=True, upload_to=acacia.data.upload.series_thumb_upload, blank=True)),
                ('limit_time', models.BooleanField(default=False, help_text=b'Beperk tijdreeks tot gegeven tijdsinterval', verbose_name=b'tijdsrestrictie')),
                ('from_limit', models.DateTimeField(null=True, verbose_name=b'Begintijd', blank=True)),
                ('to_limit', models.DateTimeField(null=True, verbose_name=b'Eindtijd', blank=True)),
                ('resample', models.CharField(choices=[(b'T', b'minuut'), (b'15T', b'kwartier'), (b'H', b'uur'), (b'D', b'dag'), (b'W', b'week'), (b'M', b'maand'), (b'A', b'jaar')], max_length=10, blank=True, help_text=b'Frequentie voor resampling van tijdreeks', null=True, verbose_name=b'frequentie')),
                ('aggregate', models.CharField(choices=[(b'mean', b'gemiddelde'), (b'max', b'maximum'), (b'min', b'minimum'), (b'sum', b'som'), (b'diff', b'verschil'), (b'first', b'eerste'), (b'last', b'laatste')], max_length=10, blank=True, help_text=b'Aggregatiemethode bij resampling van tijdreeks', null=True, verbose_name=b'aggregatie')),
                ('scale', models.FloatField(default=1.0, help_text=b'constante factor voor verschaling van de meetwaarden (v\xc3\xb3\xc3\xb3r compensatie)', verbose_name=b'verschalingsfactor')),
                ('offset', models.FloatField(default=0.0, help_text=b'constante voor compensatie van de meetwaarden (n\xc3\xa1 verschaling)', verbose_name=b'compensatieconstante')),
                ('cumsum', models.BooleanField(default=False, help_text=b'reeks transformeren naar accumulatie', verbose_name=b'accumuleren')),
                ('cumstart', models.DateTimeField(null=True, verbose_name=b'start accumulatie', blank=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Tijdreeks',
                'verbose_name_plural': 'Tijdreeksen',
            },
            bases=(models.Model, acacia.data.models.LoggerSourceMixin),
        ),
        migrations.CreateModel(
            name='SeriesProperties',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('aantal', models.IntegerField(default=0)),
                ('min', models.FloatField(default=0, null=True)),
                ('max', models.FloatField(default=0, null=True)),
                ('van', models.DateTimeField(null=True)),
                ('tot', models.DateTimeField(null=True)),
                ('gemiddelde', models.FloatField(default=0, null=True)),
                ('beforelast', models.ForeignKey(related_name='beforelast', to='data.DataPoint', null=True)),
                ('eerste', models.ForeignKey(related_name='first', to='data.DataPoint', null=True)),
                ('laatste', models.ForeignKey(related_name='last', to='data.DataPoint', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SourceFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, blank=True)),
                ('file', models.FileField(max_length=200, null=True, upload_to=acacia.data.upload.sourcefile_upload, blank=True)),
                ('rows', models.IntegerField(default=0)),
                ('cols', models.IntegerField(default=0)),
                ('start', models.DateTimeField(null=True, blank=True)),
                ('stop', models.DateTimeField(null=True, blank=True)),
                ('crc', models.IntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('uploaded', models.DateTimeField(auto_now=True)),
                ('datasource', models.ForeignKey(related_name='sourcefiles', verbose_name=b'gegevensbron', to='data.Datasource')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'bronbestand',
                'verbose_name_plural': 'bronbestanden',
            },
            bases=(models.Model, acacia.data.models.LoggerSourceMixin),
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
        migrations.CreateModel(
            name='TabGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'naam van dashboard groep', max_length=40, verbose_name=b'naam')),
                ('location', models.ForeignKey(verbose_name=b'projectlocatie', to='data.ProjectLocatie')),
            ],
            options={
                'verbose_name': 'Dashboardgroep',
                'verbose_name_plural': 'Dashboardgroepen',
            },
        ),
        migrations.CreateModel(
            name='TabPage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'basis', max_length=40, verbose_name=b'naam')),
                ('order', models.IntegerField(default=1, help_text=b'volgorde van tabblad', verbose_name=b'volgorde')),
                ('dashboard', models.ForeignKey(to='data.Dashboard')),
                ('tabgroup', models.ForeignKey(to='data.TabGroup')),
            ],
            options={
                'verbose_name': 'Tabblad',
                'verbose_name_plural': 'Tabbladen',
            },
        ),
        migrations.CreateModel(
            name='Variable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=10, verbose_name=b'variabele')),
                ('locatie', models.ForeignKey(to='data.MeetLocatie')),
            ],
            options={
                'verbose_name': 'variabele',
                'verbose_name_plural': 'variabelen',
            },
        ),
        migrations.CreateModel(
            name='Webcam',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name=b'naam')),
                ('description', models.TextField(null=True, verbose_name=b'omschrijving', blank=True)),
                ('image', models.TextField(verbose_name=b'url voor snapshot')),
                ('video', models.TextField(verbose_name=b'url voor streaming video')),
                ('admin', models.TextField(verbose_name=b'url voor beheer')),
            ],
        ),
        migrations.CreateModel(
            name='Formula',
            fields=[
                ('series_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='data.Series')),
                ('formula_text', models.TextField(null=True, verbose_name=b'berekening', blank=True)),
                ('intersect', models.BooleanField(default=True, verbose_name=b'bereken alleen voor overlappend tijdsinterval')),
            ],
            options={
                'verbose_name': 'Berekende reeks',
                'verbose_name_plural': 'Berekende reeksen',
            },
            bases=('data.series',),
        ),
        migrations.CreateModel(
            name='Grid',
            fields=[
                ('chart_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='data.Chart')),
                ('colwidth', models.FloatField(default=1, help_text=b'tijdstap in uren', verbose_name=b'tijdstap')),
                ('rowheight', models.FloatField(default=1, verbose_name=b'rijhoogte')),
                ('ymin', models.FloatField(default=0, verbose_name=b'y-minimum')),
                ('entity', models.CharField(default=b'Weerstand', max_length=50, verbose_name=b'grootheid')),
                ('unit', models.CharField(default=b'\xce\xa9m', max_length=20, verbose_name=b'eenheid', blank=True)),
                ('zmin', models.FloatField(null=True, verbose_name=b'z-minimum', blank=True)),
                ('zmax', models.FloatField(null=True, verbose_name=b'z-maximum', blank=True)),
                ('scale', models.FloatField(default=1.0, verbose_name=b'verschalingsfactor')),
            ],
            options={
                'abstract': False,
            },
            bases=('data.chart',),
        ),
        migrations.CreateModel(
            name='ManualSeries',
            fields=[
                ('series_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='data.Series')),
            ],
            options={
                'verbose_name': 'Handmatige reeks',
                'verbose_name_plural': 'Handmatige reeksen',
            },
            bases=('data.series',),
        ),
        migrations.AddField(
            model_name='variable',
            name='series',
            field=models.ForeignKey(verbose_name=b'reeks', to='data.Series'),
        ),
        migrations.AddField(
            model_name='seriesproperties',
            name='series',
            field=models.OneToOneField(related_name='properties', to='data.Series'),
        ),
        migrations.AddField(
            model_name='series',
            name='mlocatie',
            field=models.ForeignKey(verbose_name=b'meetlocatie', to='data.MeetLocatie', null=True),
        ),
        migrations.AddField(
            model_name='series',
            name='offset_series',
            field=models.ForeignKey(related_name='offset_set', blank=True, to='data.Series', help_text=b'tijdreeks voor compensatie van de meetwaarden (n\xc3\xa1 verschaling)', null=True, verbose_name=b'compensatiereeks'),
        ),
        migrations.AddField(
            model_name='series',
            name='parameter',
            field=models.ForeignKey(blank=True, to='data.Parameter', null=True),
        ),
        migrations.AddField(
            model_name='series',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_data.series_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='series',
            name='scale_series',
            field=models.ForeignKey(related_name='scaling_set', blank=True, to='data.Series', help_text=b'tijdreeks voor verschaling van de meetwaarden (v\xc3\xb3\xc3\xb3r compensatie', null=True, verbose_name=b'verschalingsreeks'),
        ),
        migrations.AddField(
            model_name='series',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='projectlocatie',
            name='dashboard',
            field=models.ForeignKey(verbose_name=b'Standaard dashboard', blank=True, to='data.TabGroup', null=True),
        ),
        migrations.AddField(
            model_name='projectlocatie',
            name='project',
            field=models.ForeignKey(to='data.Project'),
        ),
        migrations.AddField(
            model_name='projectlocatie',
            name='webcam',
            field=models.ForeignKey(blank=True, to='data.Webcam', null=True),
        ),
        migrations.AddField(
            model_name='meetlocatie',
            name='projectlocatie',
            field=models.ForeignKey(to='data.ProjectLocatie'),
        ),
        migrations.AddField(
            model_name='meetlocatie',
            name='webcam',
            field=models.ForeignKey(blank=True, to='data.Webcam', null=True),
        ),
        migrations.AddField(
            model_name='datasource',
            name='generator',
            field=models.ForeignKey(help_text=b'Generator voor het maken van tijdreeksen uit de datafiles', to='data.Generator'),
        ),
        migrations.AddField(
            model_name='datasource',
            name='meetlocatie',
            field=models.ForeignKey(related_name='datasources', to='data.MeetLocatie', help_text=b'Meetlocatie van deze gegevensbron'),
        ),
        migrations.AddField(
            model_name='datasource',
            name='user',
            field=models.ForeignKey(verbose_name=b'Aangemaakt door', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='datapoint',
            name='series',
            field=models.ForeignKey(related_name='datapoints', to='data.Series'),
        ),
        migrations.AddField(
            model_name='dashboardchart',
            name='chart',
            field=models.ForeignKey(verbose_name=b'Grafiek', to='data.Chart'),
        ),
        migrations.AddField(
            model_name='dashboardchart',
            name='dashboard',
            field=models.ForeignKey(to='data.Dashboard'),
        ),
        migrations.AddField(
            model_name='dashboard',
            name='charts',
            field=models.ManyToManyField(to='data.Chart', verbose_name=b'grafieken', through='data.DashboardChart'),
        ),
        migrations.AddField(
            model_name='dashboard',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='chartseries',
            name='chart',
            field=models.ForeignKey(related_name='series', verbose_name=b'grafiek', to='data.Chart'),
        ),
        migrations.AddField(
            model_name='chartseries',
            name='series',
            field=models.ForeignKey(verbose_name=b'tijdreeks', to='data.Series'),
        ),
        migrations.AddField(
            model_name='chartseries',
            name='series2',
            field=models.ForeignKey(related_name='series2', blank=True, to='data.Series', help_text=b'tijdreeks voor ondergrens bij area grafiek', null=True, verbose_name=b'tweede tijdreeks'),
        ),
        migrations.AddField(
            model_name='chart',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_data.chart_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='chart',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='variable',
            unique_together=set([('locatie', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='series',
            unique_together=set([('parameter', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='projectlocatie',
            unique_together=set([('project', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='parameter',
            unique_together=set([('name', 'datasource')]),
        ),
        migrations.AlterUniqueTogether(
            name='meetlocatie',
            unique_together=set([('projectlocatie', 'name')]),
        ),
        migrations.AddField(
            model_name='formula',
            name='formula_variables',
            field=models.ManyToManyField(to='data.Variable', verbose_name=b'variabelen'),
        ),
        migrations.AlterUniqueTogether(
            name='datasource',
            unique_together=set([('name', 'meetlocatie')]),
        ),
        migrations.AlterUniqueTogether(
            name='datapoint',
            unique_together=set([('series', 'date')]),
        ),
    ]
