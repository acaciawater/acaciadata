# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('validation', '0023_auto_20170920_1036'),
    ]

    operations = [
        migrations.AddField(
            model_name='validation',
            name='last_validation',
            field=models.DateTimeField(default=None, null=True, verbose_name=b'Laatste validatie', blank=True),
        ),
    ]
