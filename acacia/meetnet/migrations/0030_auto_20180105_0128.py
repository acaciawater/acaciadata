# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-05 00:28
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meetnet', '0029_remove_well_location'),
    ]

    operations = [
        migrations.RenameField(
            model_name='well',
            old_name='wgs',
            new_name='location',
        ),
    ]
