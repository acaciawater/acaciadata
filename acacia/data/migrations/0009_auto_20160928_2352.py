# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0008_data_20161012_1359'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='series',
            unique_together=set([('parameter', 'name', 'mlocatie')]),
        ),
    ]
