# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0016_auto_20161117_1501'),
        ('validation', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Validation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rule', models.ForeignKey(to='validation.Rule')),
                ('series', models.ForeignKey(to='data.Series')),
            ],
        ),
    ]
