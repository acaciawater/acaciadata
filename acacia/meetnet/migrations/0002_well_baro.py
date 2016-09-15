# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0005_auto_20160831_2337'),
        ('meetnet', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='well',
            name='baro',
            field=models.ForeignKey(blank=True, to='data.Series', help_text=b'tijdreeks voor luchtdruk compensatie', null=True, verbose_name=b'luchtdruk'),
        ),
    ]
