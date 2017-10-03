# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meetnet', '0011_auto_20170725_1103'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='loggerpos',
            name='baro',
        ),
        migrations.RemoveField(
            model_name='well',
            name='baro',
        ),
    ]
