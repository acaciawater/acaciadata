# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def copyrules(apps, schema_editor):
    Validation = apps.get_model('validation', 'Validation')
    Order = apps.get_model('validation', 'RuleOrder')
    for val in Validation.objects.all():
        order = 1
        for rule in val.rulesold.all():
            neworder = Order(rule=rule,validation=val,order=order)
            neworder.save()
            order += 1

class Migration(migrations.Migration):

    dependencies = [
        ('validation', '0020_auto_20170321_1108'),
    ]

    operations = [
        migrations.AddField(
            model_name='validation',
            name='rules',
            field=models.ManyToManyField(related_name='validations', verbose_name=b'validatieregels', through='validation.RuleOrder', to='validation.BaseRule'),
        ),
        migrations.RunPython(copyrules)
    ]
