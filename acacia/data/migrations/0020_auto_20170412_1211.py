# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0019_auto_20170329_1414'),
    ]

    operations = [
        migrations.DeleteModel(
            name='NeerslagStation',
        ),
        migrations.DeleteModel(
            name='Station',
        ),
    ]
