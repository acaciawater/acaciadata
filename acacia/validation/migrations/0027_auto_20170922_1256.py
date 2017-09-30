# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('validation', '0026_auto_20170922_1247'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rollingrule',
            name='slot',
        ),
        migrations.AlterField(
            model_name='rollingrule',
            name='count',
            field=models.PositiveIntegerField(default=10, verbose_name=b'Aantal punten'),
        ),
    ]
