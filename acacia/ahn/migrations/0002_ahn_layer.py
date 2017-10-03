# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ahn', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ahn',
            name='layer',
            field=models.CharField(default='ahn2_5m', max_length=50),
            preserve_default=False,
        ),
    ]
