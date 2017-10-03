# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0016_auto_20161117_1501'),
    ]

    operations = [
        migrations.AddField(
            model_name='seriesproperties',
            name='std',
            field=models.FloatField(default=0, null=True),
        ),
    ]
