# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2020-03-06 13:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('validation', '0037_auto_20200208_1757'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='xlbegin',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='result',
            name='xlend',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]