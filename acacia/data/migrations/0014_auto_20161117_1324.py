# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0013_sourcefile_locs'),
    ]

    operations = [
        migrations.CreateModel(
            name='BandStyle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32)),
                ('fillcolor', models.CharField(max_length=32)),
                ('fillstyle', models.CharField(default=b'solid', max_length=32)),
                ('opacity', models.FloatField(default=0.8)),
                ('borderColor', models.CharField(default=b'black', max_length=32)),
                ('borderwidth', models.IntegerField(default=0, max_length=32)),
                ('zIndex', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='LineStyle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32)),
                ('opacity', models.FloatField(default=0.8)),
                ('color', models.CharField(default=b'black', max_length=32)),
                ('dashStyle', models.CharField(default=b'Solid', max_length=32, choices=[(b'Solid', b'Standaard'), (b'Dash', b'Gestreept'), (b'Dot', b'Gestippeld')])),
                ('width', models.CharField(default=b'0', max_length=32)),
                ('zIndex', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='PlotBand',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=50)),
                ('low', models.CharField(max_length=32)),
                ('high', models.CharField(max_length=32)),
                ('repetition', models.CharField(max_length=32)),
                ('chart', models.ForeignKey(to='data.Chart')),
                ('style', models.ForeignKey(to='data.BandStyle')),
            ],
        ),
        migrations.CreateModel(
            name='PlotLine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=50)),
                ('value', models.CharField(max_length=32)),
                ('repetition', models.CharField(default=b'0', max_length=32)),
                ('chart', models.ForeignKey(to='data.Chart')),
                ('style', models.ForeignKey(to='data.LineStyle')),
            ],
        ),
        migrations.DeleteModel(
            name='NeerslagStation',
        ),
        migrations.DeleteModel(
            name='Station',
        ),
        migrations.AlterField(
            model_name='datasource',
            name='locations',
            field=models.ManyToManyField(help_text=b'Secundaire meetlocaties die deze gegevensbron gebruiken', related_name='datasources', verbose_name=b'locaties', to='data.MeetLocatie', blank=True),
        ),
        migrations.AlterField(
            model_name='keyfigure',
            name='variables',
            field=models.ManyToManyField(to='data.Variable', verbose_name=b'variabelen'),
        ),
        migrations.AlterField(
            model_name='sourcefile',
            name='cols',
            field=models.IntegerField(default=0, verbose_name=b'kolommen'),
        ),
        migrations.AlterField(
            model_name='sourcefile',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'aangemaakt'),
        ),
        migrations.AlterField(
            model_name='sourcefile',
            name='locs',
            field=models.IntegerField(default=0, verbose_name=b'locaties'),
        ),
        migrations.AlterField(
            model_name='sourcefile',
            name='rows',
            field=models.IntegerField(default=0, verbose_name=b'rijen'),
        ),
    ]
