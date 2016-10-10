# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0009_auto_20160928_2352'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='theme',
            field=models.CharField(default=b'dark-blue', choices=[(None, b'standaard'), (b'dark-blue', b'blauw'), (b'darkgreen', b'groen'), (b'gray', b'grijs'), (b'grid', b'grid'), (b'skies', b'wolken')], max_length=50, blank=True, help_text=b'Thema voor grafieken', null=True, verbose_name=b'thema'),
        ),
    ]
