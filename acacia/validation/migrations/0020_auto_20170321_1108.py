# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('validation', '0019_auto_20170301_1148'),
    ]

    operations = [
        migrations.CreateModel(
            name='RuleOrder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveSmallIntegerField(default=1)),
                ('rule', models.ForeignKey(to='validation.BaseRule')),
            ],
            options={
                'ordering': ['order'],
                'verbose_name': 'Regel',
            },
        ),
        migrations.RenameField(
            model_name='validation',
            old_name='rules',
            new_name='rulesold',
        ),
        migrations.AlterField(
            model_name='result',
            name='date',
            field=models.DateTimeField(auto_now=True, verbose_name=b'uploaded'),
        ),
        migrations.AddField(
            model_name='ruleorder',
            name='validation',
            field=models.ForeignKey(to='validation.Validation'),
        ),
    ]
