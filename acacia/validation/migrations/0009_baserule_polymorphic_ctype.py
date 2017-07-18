# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('validation', '0008_auto_20161227_1208'),
    ]

    operations = [
        migrations.AddField(
            model_name='baserule',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_validation.baserule_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
    ]
