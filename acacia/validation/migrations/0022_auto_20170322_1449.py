# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('validation', '0021_validation_rules'),
    ]

    operations = [
        migrations.CreateModel(
            name='SlotRule',
            fields=[
                ('baserule_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='validation.BaseRule')),
                ('count', models.PositiveIntegerField(default=1, verbose_name=b'Aantal')),
                ('slot', models.CharField(default=b'D', max_length=4, verbose_name=b'Eenheid', choices=[(b'H', b'uur'), (b'D', b'dag'), (b'W', b'week'), (b'M', b'maand')])),
            ],
            options={
                'verbose_name': 'Interval',
            },
            bases=('validation.baserule',),
        ),
        migrations.RemoveField(
            model_name='validation',
            name='rulesold',
        ),
        migrations.AlterField(
            model_name='nodatarule',
            name='count',
            field=models.PositiveIntegerField(default=1, verbose_name=b'Aantal'),
        ),
        migrations.AlterField(
            model_name='nodatarule',
            name='slot',
            field=models.CharField(default=b'D', max_length=4, verbose_name=b'Frequentie', choices=[(b'H', b'uur'), (b'D', b'dag'), (b'W', b'week'), (b'M', b'maand')]),
        ),
    ]
