# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    replaces = [(b'ahn', '0001_initial'), (b'ahn', '0002_ahn_layer')]

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AHN',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('resolution', models.FloatField()),
                ('url', models.URLField()),
                ('layer', models.CharField(default='ahn2_5m', max_length=50)),
            ],
        ),
    ]
