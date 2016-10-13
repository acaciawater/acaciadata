# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0011_auto_20161010_2128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datasource',
            name='locations',
            field=models.ManyToManyField(help_text=b'Secundaire meetlocaties die deze gegevensbron gebruiken', related_name='datasources', verbose_name=b'Secundaire meetlocaties', to='data.MeetLocatie', blank=True),
        ),
    ]
