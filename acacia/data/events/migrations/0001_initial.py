# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action', models.IntegerField(default=0, choices=[(0, b'ignore'), (1, b'email'), (2, b'sms')])),
                ('message', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now=True)),
                ('state', models.IntegerField(default=1, choices=[(0, b'off'), (1, b'on')])),
                ('message', models.TextField()),
                ('sent', models.BooleanField(default=False)),
                ('event', models.ForeignKey(to='events.Event')),
            ],
            options={
                'verbose_name': 'Geschiedenis',
                'verbose_name_plural': 'Geschiedenis',
            },
        ),
        migrations.CreateModel(
            name='Target',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cellphone', models.CharField(max_length=12)),
                ('email', models.EmailField(max_length=254)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Trigger',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=b'naam')),
                ('hilo', models.CharField(default=b'>', help_text=b'onder of bovengrens', max_length=1, verbose_name=b'grens', choices=[(b'>', b'boven'), (b'<', b'onder')])),
                ('level', models.FloatField(verbose_name=b'grenswaarde')),
                ('freq', models.CharField(choices=[(b'T', b'minuut'), (b'15T', b'kwartier'), (b'H', b'uur'), (b'D', b'dag'), (b'W', b'week'), (b'M', b'maand'), (b'A', b'jaar')], max_length=8, blank=True, help_text=b'frequentie voor resampling', null=True, verbose_name=b'frequentie')),
                ('how', models.CharField(choices=[(b'mean', b'gemiddelde'), (b'median', b'mediaan'), (b'max', b'maximum'), (b'min', b'minimum'), (b'sum', b'som')], max_length=16, blank=True, help_text=b'methode van aggregatie', null=True, verbose_name=b'methode')),
                ('window', models.IntegerField(default=1, help_text=b'grootte van de groep', verbose_name=b'groep')),
                ('count', models.IntegerField(default=1, help_text=b'minimum aantal punten', verbose_name=b'aantal')),
                ('series', models.ForeignKey(verbose_name=b'tijdreeks', to='data.Series')),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='target',
            field=models.ForeignKey(to='events.Target'),
        ),
        migrations.AddField(
            model_name='event',
            name='trigger',
            field=models.ForeignKey(to='events.Trigger'),
        ),
    ]
