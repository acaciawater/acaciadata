# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0007_auto_20160927_1710'),
    ]

    operations = [
        migrations.AddField(
            model_name='generator',
            name='url',
            field=models.URLField(null=True, verbose_name=b'Default url', blank=True),
        ),
        migrations.AlterField(
            model_name='datasource',
            name='locations',
            field=models.ManyToManyField(help_text=b'Secundaire meetlocaties die deze gegevensbron gebruiken', related_name='datasources', verbose_name=b'Secundaire meetlocaties', to='data.MeetLocatie'),
        ),
        migrations.AlterField(
            model_name='datasource',
            name='meetlocatie',
            field=models.ForeignKey(verbose_name=b'Primaire meetlocatie', to='data.MeetLocatie', help_text=b'Primaire meetlocatie van deze gegevensbron'),
        ),
    ]
