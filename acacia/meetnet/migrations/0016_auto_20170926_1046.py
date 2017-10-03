# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meetnet', '0015_loggerstat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loggerstat',
            name='count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='loggerstat',
            name='max',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='loggerstat',
            name='min',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='loggerstat',
            name='p10',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='loggerstat',
            name='p50',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='loggerstat',
            name='p90',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='loggerstat',
            name='std',
            field=models.FloatField(default=0),
        ),
    ]
