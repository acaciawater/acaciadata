# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0015_auto_20161117_1403'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bandstyle',
            old_name='borderColor',
            new_name='bordercolor',
        ),
        migrations.RenameField(
            model_name='linestyle',
            old_name='dashStyle',
            new_name='dashstyle',
        ),
        migrations.RemoveField(
            model_name='bandstyle',
            name='fillstyle',
        ),
        migrations.RemoveField(
            model_name='bandstyle',
            name='opacity',
        ),
        migrations.RemoveField(
            model_name='linestyle',
            name='opacity',
        ),
        migrations.AddField(
            model_name='plotband',
            name='axis',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='plotline',
            name='axis',
            field=models.IntegerField(default=1),
        ),
    ]
