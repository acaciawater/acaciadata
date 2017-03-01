# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    replaces = [(b'validation', '0001_initial')]

    dependencies = [
        ('data', '0016_auto_20161117_1501'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True)),
                ('value', models.FloatField(default=None, null=True)),
                ('comp', models.CharField(default=b'GT', max_length=2, choices=[(b'GT', b'boven'), (b'LT', b'onder'), (b'EQ', b'gelijk'), (b'NE', b'ongelijk')])),
                ('series', models.ForeignKey(default=None, to='data.Series', null=True)),
            ],
        ),
    ]
