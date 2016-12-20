# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gwsforecast', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gwsforecast',
            name='forec_et',
            field=models.ForeignKey(related_name='forec_et', to='data.Series'),
        ),
        migrations.AlterField(
            model_name='gwsforecast',
            name='forec_pt',
            field=models.ForeignKey(related_name='forec_pt', to='data.Series'),
        ),
        migrations.AlterField(
            model_name='gwsforecast',
            name='forec_tmp',
            field=models.ForeignKey(related_name='forec_tmp', to='data.Series'),
        ),
        migrations.AlterField(
            model_name='gwsforecast',
            name='hist_ev',
            field=models.ForeignKey(related_name='hist_ev', to='data.Series'),
        ),
        migrations.AlterField(
            model_name='gwsforecast',
            name='hist_pt',
            field=models.ForeignKey(related_name='hist_pt', to='data.Series'),
        ),
    ]
