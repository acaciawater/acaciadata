# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-31 20:26
from __future__ import unicode_literals

from django.db import migrations
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('meetnet', '0020_auto_20171027_1047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='photo',
            field=sorl.thumbnail.fields.ImageField(upload_to=b'fotos'),
        ),
    ]