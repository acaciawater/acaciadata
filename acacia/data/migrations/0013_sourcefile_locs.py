# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0012_auto_20161011_0954'),
    ]

    operations = [
        migrations.AddField(
            model_name='sourcefile',
            name='locs',
            field=models.IntegerField(default=0),
        ),
    ]
