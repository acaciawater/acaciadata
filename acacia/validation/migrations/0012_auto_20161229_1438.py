# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('validation', '0011_auto_20161227_1301'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='nodatarule',
            options={'verbose_name': 'Aantal'},
        ),
        migrations.RemoveField(
            model_name='validpoint',
            name='point',
        ),
        migrations.AddField(
            model_name='validpoint',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2016, 12, 29, 14, 38, 4, 299013, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='diffrule',
            name='tolerance',
            field=models.FloatField(default=3, help_text=b'verschil plus of min x maal de standaardafwijking', verbose_name=b'tolerantie'),
        ),
        migrations.AlterField(
            model_name='validation',
            name='rules',
            field=models.ManyToManyField(to='validation.BaseRule', verbose_name=b'validatieregels'),
        ),
        migrations.AlterField(
            model_name='validation',
            name='series',
            field=models.ForeignKey(verbose_name=b'tijdreeks', to='data.Series'),
        ),
        migrations.AlterField(
            model_name='validationresult',
            name='validation',
            field=models.ForeignKey(verbose_name=b'validatie', to='validation.Validation'),
        ),
        migrations.AlterField(
            model_name='validpoint',
            name='value',
            field=models.FloatField(default=None, null=True),
        ),
    ]
