# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('validation', '0005_auto_20161129_1255'),
    ]

    operations = [
        migrations.AlterField(
            model_name='validpoint',
            name='value',
            field=models.FloatField(null=True),
        ),
    ]
