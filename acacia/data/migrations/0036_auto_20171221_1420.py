# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-21 11:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0035_merge_20171220_1131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plotband',
            name='orientation',
            field=models.CharField(choices=[(b'h', 'horizontaal'), (b'v', 'vertikaal')], max_length=1, verbose_name='orientatie'),
        ),
        migrations.AlterField(
            model_name='plotline',
            name='orientation',
            field=models.CharField(choices=[(b'h', 'horizontaal'), (b'v', 'vertikaal')], max_length=1, verbose_name='orientatie'),
        ),
        migrations.AlterField(
            model_name='series',
            name='offset',
            field=models.FloatField(default=0.0, help_text='constante voor compensatie van de meetwaarden (na verschaling)', verbose_name='compensatieconstante'),
        ),
        migrations.AlterField(
            model_name='series',
            name='offset_series',
            field=models.ForeignKey(blank=True, help_text='tijdreeks voor compensatie van de meetwaarden (na verschaling)', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='offset_set', to='data.Series', verbose_name='compensatiereeks'),
        ),
        migrations.AlterField(
            model_name='series',
            name='scale',
            field=models.FloatField(default=1.0, help_text='constante factor voor verschaling van de meetwaarden (voor compensatie)', verbose_name='verschalingsfactor'),
        ),
        migrations.AlterField(
            model_name='series',
            name='scale_series',
            field=models.ForeignKey(blank=True, help_text='tijdreeks voor verschaling van de meetwaarden (voor compensatie)', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='scaling_set', to='data.Series', verbose_name='verschalingsreeks'),
        ),
    ]
