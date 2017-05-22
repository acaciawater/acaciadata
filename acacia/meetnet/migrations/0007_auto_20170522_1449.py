# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meetnet', '0006_auto_20170522_1433'),
    ]

    operations = [
        migrations.AlterField(
            model_name='well',
            name='ahn3',
            field=models.DecimalField(decimal_places=2, max_digits=10, blank=True, help_text=b'AHN3-maaiveld in meter tov NAP', null=True, verbose_name=b'AHN3 maaiveld'),
        ),
    ]
