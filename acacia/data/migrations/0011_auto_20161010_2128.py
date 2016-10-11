# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0010_auto_20161008_2023'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datasource',
            name='locations',
            field=models.ManyToManyField(related_name='datasources', to='data.MeetLocatie', blank=True, help_text=b'Secundaire meetlocaties die deze gegevensbron gebruiken', null=True, verbose_name=b'Secundaire meetlocaties'),
        ),
        migrations.AlterField(
            model_name='datasource',
            name='meetlocatie',
            field=models.ForeignKey(blank=True, to='data.MeetLocatie', help_text=b'Primaire meetlocatie van deze gegevensbron', null=True, verbose_name=b'Primaire meetlocatie'),
        ),
        migrations.AlterField(
            model_name='project',
            name='theme',
            field=models.CharField(default=b'dark-blue', choices=[(None, b'standaard'), (b'dark-blue', b'blauw'), (b'dark-green', b'groen'), (b'gray', b'grijs'), (b'grid', b'grid'), (b'skies', b'wolken')], max_length=50, blank=True, help_text=b'Thema voor grafieken', null=True, verbose_name=b'thema'),
        ),
    ]
