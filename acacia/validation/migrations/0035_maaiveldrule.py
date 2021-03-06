# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-07-30 11:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('meetnet', '0035_auto_20190730_1321'),
        ('validation', '0034_merge_20190725_1348'),
    ]

    operations = [
        migrations.CreateModel(
            name='MaaiveldRule',
            fields=[
                ('baserule_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='validation.BaseRule')),
                ('well', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meetnet.Well', verbose_name='put')),
            ],
            options={
                'verbose_name': 'maaiveld regel',
            },
            bases=('validation.baserule',),
        ),
    ]
