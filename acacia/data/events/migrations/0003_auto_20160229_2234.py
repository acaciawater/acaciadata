# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0002_fix_contenttypes'),
        ('events', '0002_add_message'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trigger',
            name='series',
        ),
        migrations.AddField(
            model_name='event',
            name='series',
            field=models.ForeignKey(default=None, verbose_name=b'tijdreeks', to='data.Series'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='trigger',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='action',
            field=models.IntegerField(default=0, verbose_name=b'actie', choices=[(0, b'negeren'), (1, b'email'), (2, b'sms')]),
        ),
        migrations.AlterField(
            model_name='event',
            name='message',
            field=models.TextField(null=True, verbose_name=b'Standaard bericht', blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='target',
            field=models.ForeignKey(verbose_name=b'ontvanger', to='events.Target'),
        ),
    ]
