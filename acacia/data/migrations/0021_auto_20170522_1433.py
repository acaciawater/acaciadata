# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0020_auto_20170412_1211'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datasource',
            name='timezone',
            field=models.CharField(default=b'CET', max_length=50, verbose_name=b'Tijzone', blank=True),
        ),
    ]
