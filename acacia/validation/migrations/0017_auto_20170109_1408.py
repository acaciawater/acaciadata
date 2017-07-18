# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('validation', '0016_auto_20170109_1103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='validation',
            name='series',
            field=models.OneToOneField(verbose_name=b'tijdreeks', to='data.Series'),
        ),
    ]
