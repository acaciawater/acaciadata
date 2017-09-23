# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('validation', '0025_auto_20170921_1722'),
    ]

    operations = [
        migrations.CreateModel(
            name='RollingRule',
            fields=[
                ('outlierrule_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='validation.OutlierRule')),
                ('slot', models.CharField(default=b'D', max_length=10, verbose_name=b'Periode', choices=[(b'T', b'minuut'), (b'H', b'uur'), (b'D', b'dag'), (b'W', b'week'), (b'M', b'maand')])),
                ('count', models.PositiveIntegerField(default=1, verbose_name=b'Lengte')),
            ],
            options={
                'verbose_name': 'Locale Uitbijter',
            },
            bases=('validation.outlierrule',),
        ),
        migrations.AlterModelOptions(
            name='diffrule',
            options={'verbose_name': 'Lokale verandering'},
        ),
    ]
