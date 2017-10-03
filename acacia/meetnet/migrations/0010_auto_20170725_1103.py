# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('meetnet', '0009_auto_20170725_0931'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='meteodata',
            options={'verbose_name': 'Meteo', 'verbose_name_plural': 'Meteo'},
        ),
        migrations.AlterField(
            model_name='meteodata',
            name='baro',
            field=models.ForeignKey(related_name='well_baro', on_delete=django.db.models.deletion.SET_NULL, verbose_name=b'Luchtdruk', blank=True, to='data.Series', null=True),
        ),
        migrations.AlterField(
            model_name='meteodata',
            name='well',
            field=models.OneToOneField(related_name='meteo', verbose_name=b'put', to='meetnet.Well'),
        ),
    ]
