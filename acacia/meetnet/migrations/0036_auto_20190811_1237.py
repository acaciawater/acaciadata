# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-08-11 10:37
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meetnet', '0035_auto_20190730_1321'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Handpeiling',
            new_name='Handpeilingen',
        ),
        migrations.AlterModelOptions(
            name='handpeilingen',
            options={'verbose_name': 'Handpeilingen', 'verbose_name_plural': 'Handpeilingen'},
        ),
    ]
