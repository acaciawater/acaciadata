# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('validation', '0010_auto_20161227_1242'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rule',
            name='series',
        ),
        migrations.AlterModelOptions(
            name='baserule',
            options={'verbose_name': 'regel'},
        ),
        migrations.AlterField(
            model_name='validation',
            name='rules',
            field=models.ManyToManyField(to='validation.BaseRule'),
        ),
        migrations.DeleteModel(
            name='Rule',
        ),
    ]
