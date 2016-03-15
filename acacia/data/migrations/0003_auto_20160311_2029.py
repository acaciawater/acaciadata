# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0002_fix_contenttypes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chart',
            name='name',
            field=models.CharField(max_length=100, verbose_name=b'naam'),
        ),
        migrations.AlterField(
            model_name='chart',
            name='title',
            field=models.CharField(max_length=100, verbose_name=b'titel'),
        ),
        migrations.AlterField(
            model_name='chartseries',
            name='name',
            field=models.CharField(max_length=100, null=True, verbose_name=b'legendanaam', blank=True),
        ),
        migrations.AlterField(
            model_name='dashboard',
            name='name',
            field=models.CharField(max_length=100, verbose_name=b'naam'),
        ),
        migrations.AlterField(
            model_name='datasource',
            name='name',
            field=models.CharField(max_length=100, verbose_name=b'naam'),
        ),
        migrations.AlterField(
            model_name='meetlocatie',
            name='name',
            field=models.CharField(max_length=100, verbose_name=b'naam'),
        ),
        migrations.AlterField(
            model_name='projectlocatie',
            name='name',
            field=models.CharField(max_length=100, verbose_name=b'naam'),
        ),
        migrations.AlterField(
            model_name='series',
            name='name',
            field=models.CharField(max_length=100, verbose_name=b'naam'),
        ),
        migrations.AlterField(
            model_name='sourcefile',
            name='name',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AlterField(
            model_name='tabgroup',
            name='name',
            field=models.CharField(help_text=b'naam van dashboard groep', max_length=50, verbose_name=b'naam'),
        ),
        migrations.AlterField(
            model_name='tabpage',
            name='name',
            field=models.CharField(default=b'basis', max_length=50, verbose_name=b'naam'),
        ),
        migrations.AlterField(
            model_name='variable',
            name='name',
            field=models.CharField(max_length=20, verbose_name=b'variabele'),
        ),
    ]
