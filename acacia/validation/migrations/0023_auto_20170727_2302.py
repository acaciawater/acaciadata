# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('validation', '0022_auto_20170322_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nodatarule',
            name='slot',
            field=models.CharField(default=b'D', max_length=10, verbose_name=b'Frequentie', choices=[(b'T', b'minuut'), (b'H', b'uur'), (b'D', b'dag'), (b'W', b'week'), (b'M', b'maand')]),
        ),
        migrations.AlterField(
            model_name='slotrule',
            name='slot',
            field=models.CharField(default=b'D', max_length=4, verbose_name=b'Eenheid', choices=[(b'T', b'minuut'), (b'H', b'uur'), (b'D', b'dag'), (b'W', b'week'), (b'M', b'maand')]),
        ),
    ]
