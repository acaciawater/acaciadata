# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('validation', '0002_validation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rule',
            name='series',
            field=models.ForeignKey(default=None, blank=True, to='data.Series', null=True),
        ),
        migrations.AlterField(
            model_name='rule',
            name='value',
            field=models.FloatField(default=None, null=True, blank=True),
        ),
    ]
