# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('validation', '0013_auto_20161230_1333'),
    ]

    operations = [
        migrations.AddField(
            model_name='seriesrule',
            name='constant',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='seriesrule',
            name='factor',
            field=models.FloatField(default=1),
        ),
    ]
