# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meetnet', '0013_handpeiling'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monfile',
            name='instrument_number',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
