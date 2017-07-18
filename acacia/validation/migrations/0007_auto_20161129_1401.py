# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('validation', '0006_auto_20161129_1310'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='validation',
            name='rule',
        ),
        migrations.AddField(
            model_name='validation',
            name='rules',
            field=models.ManyToManyField(to='validation.Rule'),
        ),
    ]
