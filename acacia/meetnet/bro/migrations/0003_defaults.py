# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-12-10 12:26
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('meetnet', '0042_compoundseries'),
        ('bro', '0002_auto_20191207_1419'),
    ]

    operations = [
        migrations.CreateModel(
            name='Defaults',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deliveryAccountableParty', models.CharField(help_text='KVK nummer van data leverancier', max_length=8, validators=[django.core.validators.RegexValidator(message='Illegal chamber of commerce number', regex=b'\\d{8}')], verbose_name='deliveryAccountableParty')),
                ('owner', models.CharField(help_text=b'KVK-nummer van de eigenaar', max_length=8, validators=[django.core.validators.RegexValidator(message='Illegal chamber of commerce number', regex=b'\\d{8}')], verbose_name='Owner')),
                ('maintenanceResponsibleParty', models.CharField(blank=True, max_length=8, null=True, validators=[django.core.validators.RegexValidator(message='Illegal chamber of commerce number', regex=b'\\d{8}')], verbose_name='Onderhoudende instantie')),
                ('network', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='bro', to='meetnet.Network', verbose_name='Network')),
            ],
            options={
                'verbose_name': 'Defaults',
                'verbose_name_plural': 'Defaults',
            },
        ),
    ]
