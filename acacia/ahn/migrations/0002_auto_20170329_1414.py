# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ahn', '0001_squashed_0002_ahn_layer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ahn',
            name='layer',
            field=models.CharField(max_length=50),
        ),
    ]
