# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0022_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='series',
            name='timezone',
            field=models.CharField(max_length=20, blank=True),
        ),
        migrations.AlterField(
            model_name='datasource',
            name='timezone',
            field=models.CharField(default=b'Europe/Amsterdam', max_length=50, verbose_name=b'Tijdzone', blank=True),
        ),
        migrations.AlterField(
            model_name='series',
            name='mlocatie',
            field=models.ForeignKey(verbose_name=b'meetlocatie', blank=True, to='data.MeetLocatie', null=True),
        ),
    ]
