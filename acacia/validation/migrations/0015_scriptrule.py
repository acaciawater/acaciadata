# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('validation', '0014_auto_20170104_1528'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScriptRule',
            fields=[
                ('baserule_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='validation.BaseRule')),
                ('script', models.TextField(default=b'return self.compare(target,0)')),
            ],
            options={
                'verbose_name': 'Python script',
            },
            bases=('validation.baserule',),
        ),
    ]
