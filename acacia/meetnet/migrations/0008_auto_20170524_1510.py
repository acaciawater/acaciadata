# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meetnet', '0007_auto_20170522_1449'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='well',
            name='ahn3',
        ),
        migrations.AddField(
            model_name='well',
            name='ahn',
            field=models.DecimalField(decimal_places=2, max_digits=10, blank=True, help_text=b'AHN-maaiveld in meter tov NAP', null=True, verbose_name=b'AHN maaiveld'),
        ),
    ]
