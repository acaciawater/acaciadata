# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('data', '0016_auto_20161117_1501'),
        ('validation', '0003_auto_20161124_1259'),
    ]

    operations = [
        migrations.CreateModel(
            name='ValidationResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('begin', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('status', models.CharField(default=b'P', max_length=1, choices=[(b'P', b'pending'), (b'A', b'accepted'), (b'R', b'rejected')])),
                ('remarks', models.TextField(null=True, blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('validation', models.ForeignKey(to='validation.Validation')),
            ],
        ),
        migrations.CreateModel(
            name='ValidPoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('valid', models.BooleanField()),
                ('point', models.ForeignKey(to='data.DataPoint')),
                ('validation', models.ForeignKey(to='validation.Validation')),
            ],
        ),
    ]
