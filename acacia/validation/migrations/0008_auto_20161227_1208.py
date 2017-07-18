# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0016_auto_20161117_1501'),
        ('validation', '0007_auto_20161129_1401'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseRule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name=b'naam')),
                ('description', models.TextField(verbose_name=b'omschrijving', blank=True)),
                ('comp', models.CharField(default=b'GT', max_length=2, verbose_name=b'vergelijking', choices=[(b'GT', b'boven'), (b'LT', b'onder'), (b'EQ', b'gelijk'), (b'NE', b'ongelijk')])),
            ],
        ),
        migrations.AlterModelOptions(
            name='rule',
            options={'verbose_name': 'regel', 'verbose_name_plural': 'regels'},
        ),
        migrations.AlterModelOptions(
            name='validation',
            options={'verbose_name': 'validatie', 'verbose_name_plural': 'validaties'},
        ),
        migrations.AlterModelOptions(
            name='validationresult',
            options={'verbose_name': 'resultaat', 'verbose_name_plural': 'resultaten'},
        ),
        migrations.AlterField(
            model_name='rule',
            name='comp',
            field=models.CharField(default=b'GT', max_length=2, verbose_name=b'vergelijking', choices=[(b'GT', b'boven'), (b'LT', b'onder'), (b'EQ', b'gelijk'), (b'NE', b'ongelijk')]),
        ),
        migrations.AlterField(
            model_name='rule',
            name='description',
            field=models.TextField(verbose_name=b'omschrijving', blank=True),
        ),
        migrations.AlterField(
            model_name='rule',
            name='name',
            field=models.CharField(max_length=50, verbose_name=b'naam'),
        ),
        migrations.AlterField(
            model_name='rule',
            name='series',
            field=models.ForeignKey(default=None, to='data.Series', blank=True, help_text=b'validatie tijdreeks', null=True, verbose_name=b'tijdreeks'),
        ),
        migrations.AlterField(
            model_name='rule',
            name='value',
            field=models.FloatField(default=None, help_text=b'vaste validatiewaarde waarde (criterium)', null=True, verbose_name=b'waarde', blank=True),
        ),
        migrations.CreateModel(
            name='DiffRule',
            fields=[
                ('baserule_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='validation.BaseRule')),
            ],
            bases=('validation.baserule',),
        ),
        migrations.CreateModel(
            name='NoDataRule',
            fields=[
                ('baserule_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='validation.BaseRule')),
                ('slot', models.CharField(default=b'D', max_length=4)),
                ('count', models.PositiveIntegerField(default=1)),
            ],
            bases=('validation.baserule',),
        ),
        migrations.CreateModel(
            name='OutlierRule',
            fields=[
                ('baserule_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='validation.BaseRule')),
            ],
            bases=('validation.baserule',),
        ),
        migrations.CreateModel(
            name='SeriesRule',
            fields=[
                ('baserule_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='validation.BaseRule')),
                ('series', models.ForeignKey(default=None, to='data.Series', blank=True, help_text=b'validatie tijdreeks', null=True, verbose_name=b'tijdreeks')),
            ],
            bases=('validation.baserule',),
        ),
        migrations.CreateModel(
            name='ValueRule',
            fields=[
                ('baserule_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='validation.BaseRule')),
                ('value', models.FloatField(default=None, help_text=b'validatiewaarde waarde', null=True, verbose_name=b'waarde', blank=True)),
            ],
            bases=('validation.baserule',),
        ),
    ]
