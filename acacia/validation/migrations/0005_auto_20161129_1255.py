# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('validation', '0004_validationresult_validpoint'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='validationresult',
            name='status',
        ),
        migrations.RemoveField(
            model_name='validpoint',
            name='valid',
        ),
        migrations.AddField(
            model_name='validationresult',
            name='xlfile',
            field=models.FileField(default='aap.xlsx', upload_to=b'valid'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='validpoint',
            name='value',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
