# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('validation', '0024_validation_last_validation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scriptrule',
            name='script',
            field=models.TextField(default=b"print 'running validation script ' + unicode(self)\nresult = (target,self.compare(target, 0))"),
        ),
    ]
