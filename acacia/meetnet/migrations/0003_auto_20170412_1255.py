# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0020_auto_20170412_1211'),
        ('meetnet', '0002_well_baro'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='loggerpos',
            options={'ordering': ['start_date', 'logger'], 'verbose_name': 'DataloggerInstallatie'},
        ),
        migrations.AddField(
            model_name='screen',
            name='mloc',
            field=models.ForeignKey(blank=True, to='data.MeetLocatie', null=True),
        ),
        migrations.AddField(
            model_name='well',
            name='ploc',
            field=models.ForeignKey(blank=True, to='data.ProjectLocatie', null=True),
        ),
    ]
