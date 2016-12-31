# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0017_seriesproperties_std'),
    ]

    operations = [
        migrations.RenameField(
            model_name='seriesproperties',
            old_name='std',
            new_name='stddev',
        ),
    ]
