# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0006_neerslagstation_station'),
    ]

    operations = [
        migrations.DeleteModel(
            name='NeerslagStation',
        ),
        migrations.DeleteModel(
            name='Station',
        ),
    ]
