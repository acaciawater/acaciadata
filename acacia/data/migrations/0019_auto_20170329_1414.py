# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0018_neerslagstation_station'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meetlocatie',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(help_text=b'Meetlocatie in Rijksdriehoekstelsel coordinaten', srid=28992, verbose_name=b'locatie'),
        ),
    ]
