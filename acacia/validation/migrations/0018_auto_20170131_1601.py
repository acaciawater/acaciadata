# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('validation', '0017_auto_20170109_1408'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='valid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='validation',
            name='users',
            field=models.ManyToManyField(help_text=b'Gebruikers die emails ontvangen over validatie', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='result',
            name='validation',
            field=models.OneToOneField(verbose_name=b'validatie', to='validation.Validation'),
        ),
        migrations.AlterField(
            model_name='result',
            name='xlfile',
            field=models.FileField(null=True, upload_to=b'valid', blank=True),
        ),
    ]
