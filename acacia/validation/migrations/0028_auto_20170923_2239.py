# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('validation', '0027_auto_20170922_1256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rollingrule',
            name='count',
            field=models.PositiveIntegerField(default=3, verbose_name=b'Aantal punten'),
        ),
    ]
