# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meetnet', '0004_auto_20170412_1256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datalogger',
            name='model',
            field=models.CharField(default=b'14', max_length=50, verbose_name=b'type', choices=[(b'micro', b'Micro-Diver'), (b'3', b'TD-Diver'), (b'ctd', b'CTD-Diver'), (b'16', b'Cera-Diver'), (b'14', b'Mini-Diver'), (b'baro', b'Baro-Diver'), (b'etd', b'ElliTrack-D'), (b'etd2', b'ElliTrack-D2')]),
        ),
        migrations.AlterField(
            model_name='well',
            name='name',
            field=models.CharField(max_length=50, verbose_name=b'naam'),
        ),
        migrations.AlterField(
            model_name='well',
            name='nitg',
            field=models.CharField(unique=True, max_length=50, verbose_name=b'TNO/NITG nummer', blank=True),
        ),
    ]
