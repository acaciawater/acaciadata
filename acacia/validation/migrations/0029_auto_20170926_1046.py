# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('validation', '0028_auto_20170923_2239'),
    ]

    operations = [
        migrations.CreateModel(
            name='RangeRule',
            fields=[
                ('baserule_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='validation.BaseRule')),
                ('upper', models.FloatField(verbose_name=b'Bovengrens')),
                ('lower', models.FloatField(verbose_name=b'Ondergrens')),
                ('inclusive', models.BooleanField(default=True, verbose_name=b'inclusief')),
            ],
            options={
                'verbose_name': 'Bereik',
            },
            bases=('validation.baserule',),
        ),
        migrations.AlterModelOptions(
            name='baserule',
            options={'ordering': ('name',), 'verbose_name': 'regel'},
        ),
        migrations.AlterModelOptions(
            name='validation',
            options={'ordering': ('series',), 'verbose_name': 'validatie', 'verbose_name_plural': 'validaties'},
        ),
    ]
