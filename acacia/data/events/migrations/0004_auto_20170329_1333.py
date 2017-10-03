# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_auto_20160229_2234'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='target',
            options={'verbose_name': 'ontvanger'},
        ),
    ]
