# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meetnet', '0005_auto_20170522_0026'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='well',
            options={'ordering': ['nitg', 'name'], 'verbose_name': 'put', 'verbose_name_plural': 'putten'},
        ),
        migrations.AddField(
            model_name='well',
            name='ahn3',
            field=models.DecimalField(decimal_places=1, max_digits=10, blank=True, help_text=b'AHN3-maaiveld in meter tov NAP', null=True, verbose_name=b'AHN3 maaiveld'),
        ),
    ]
