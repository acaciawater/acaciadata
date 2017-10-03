# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('validation', '0029_auto_20170926_1046'),
    ]

    operations = [
        migrations.AddField(
            model_name='diffrule',
            name='direction',
            field=models.CharField(default=b'b', max_length=1, verbose_name=b'kijkrichting', choices=[(b'f', b'Vooruit'), (b'b', b'Achteruit')]),
        ),
    ]
