# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('validation', '0030_diffrule_direction'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='diffrule',
            options={'verbose_name': 'Verschil'},
        ),
    ]
