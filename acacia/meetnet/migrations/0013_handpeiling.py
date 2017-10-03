# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0023_auto_20170918_0135'),
        ('meetnet', '0012_auto_20170725_1108'),
    ]

    operations = [
        migrations.CreateModel(
            name='Handpeiling',
            fields=[
                ('manualseries_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='data.ManualSeries')),
                ('refpnt', models.CharField(default=b'bkb', max_length=4, verbose_name=b'referentie', choices=[(b'bkb', b'Bovenkant buis'), (b'nap', b'NAP')])),
            ],
            options={
                'verbose_name': 'Handpeiling',
                'verbose_name_plural': 'Handpeilngen',
            },
            bases=('data.manualseries',),
        ),
    ]
