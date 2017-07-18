# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('validation', '0012_auto_20161229_1438'),
    ]

    operations = [
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('begin', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('xlfile', models.FileField(upload_to=b'valid')),
                ('remarks', models.TextField(null=True, blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('validation', models.ForeignKey(verbose_name=b'validatie', to='validation.Validation')),
            ],
            options={
                'verbose_name': 'resultaat',
                'verbose_name_plural': 'resultaten',
            },
        ),
        migrations.CreateModel(
            name='SubResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('valid', models.PositiveIntegerField()),
                ('invalid', models.PositiveIntegerField()),
                ('first_invalid', models.DateTimeField(null=True)),
                ('message', models.TextField(null=True, blank=True)),
                ('rule', models.ForeignKey(to='validation.BaseRule')),
                ('validation', models.ForeignKey(to='validation.Validation')),
            ],
            options={
                'verbose_name': 'tussenresultaat',
                'verbose_name_plural': 'tussenresultaten',
            },
        ),
        migrations.RemoveField(
            model_name='validationresult',
            name='user',
        ),
        migrations.RemoveField(
            model_name='validationresult',
            name='validation',
        ),
        migrations.AlterField(
            model_name='nodatarule',
            name='slot',
            field=models.CharField(default=b'D', max_length=4, choices=[(b'H', b'uur'), (b'D', b'dag'), (b'W', b'week'), (b'M', b'maand')]),
        ),
        migrations.DeleteModel(
            name='ValidationResult',
        ),
    ]
