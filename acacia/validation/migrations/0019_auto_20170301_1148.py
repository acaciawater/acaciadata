# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('validation', '0018_auto_20170131_1601'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2017, 3, 1, 11, 48, 1, 963641, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='validation',
            name='users',
            field=models.ManyToManyField(help_text=b'Gebruikers die emails ontvangen over validatie', to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
