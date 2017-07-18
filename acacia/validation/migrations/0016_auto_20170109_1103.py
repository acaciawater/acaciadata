# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('validation', '0015_scriptrule'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scriptrule',
            name='script',
            field=models.TextField(default=b"print 'running validation script ' + str(self)\nresult = (target,self.compare(target, 0))"),
        ),
    ]
