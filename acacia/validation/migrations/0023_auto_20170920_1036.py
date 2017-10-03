# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('validation', '0022_auto_20170322_1449'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChangeRule',
            fields=[
                ('baserule_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='validation.BaseRule')),
                ('freq', models.CharField(default=b'D', max_length=4, verbose_name=b'frequentie', choices=[(b'T', b'minuut'), (b'H', b'uur'), (b'D', b'dag'), (b'W', b'week'), (b'M', b'maand')])),
                ('periods', models.PositiveIntegerField(default=1, help_text=b'aantal periodes vooruit', verbose_name=b'periode')),
                ('change', models.FloatField(default=0, help_text=b'procentuele verandering', verbose_name=b'verandering')),
            ],
            options={
                'verbose_name': 'Verandering',
            },
            bases=('validation.baserule',),
        ),
        migrations.AddField(
            model_name='validation',
            name='valid',
            field=models.NullBooleanField(default=None, verbose_name=b'Valide'),
        ),
        migrations.AddField(
            model_name='validation',
            name='validated',
            field=models.BooleanField(default=False, verbose_name=b'Gevalideerd'),
        ),
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
