# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meetnet', '0014_auto_20170921_1722'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoggerStat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.PositiveIntegerField()),
                ('min', models.FloatField()),
                ('p10', models.FloatField()),
                ('p50', models.FloatField()),
                ('p90', models.FloatField()),
                ('max', models.FloatField()),
                ('std', models.FloatField()),
                ('loggerpos', models.OneToOneField(to='meetnet.LoggerPos')),
            ],
        ),
    ]
