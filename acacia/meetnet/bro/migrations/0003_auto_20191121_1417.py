# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-11-21 13:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bro', '0002_auto_20191119_2306'),
    ]

    operations = [
        migrations.RenameField(
            model_name='code',
            old_name='default_value',
            new_name='is_default',
        ),
    ]