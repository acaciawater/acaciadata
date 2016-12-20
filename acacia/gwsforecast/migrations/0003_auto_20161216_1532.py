# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0007_auto_20161117_1106'),
        ('gwsforecast', '0002_auto_20161118_0833'),
    ]

    operations = [
        migrations.AddField(
            model_name='gwsforecast',
            name='forec_et_std',
            field=models.ForeignKey(related_name='forec_et_std', default=None, to='data.Series'),
        ),
        migrations.AddField(
            model_name='gwsforecast',
            name='forec_pt_std',
            field=models.ForeignKey(related_name='forec_pt_std', default=None, to='data.Series'),
        ),
        migrations.AddField(
            model_name='gwsforecast',
            name='forec_tmp_std',
            field=models.ForeignKey(related_name='forec_tmp_std', default=None, to='data.Series'),
        ),
        migrations.AlterField(
            model_name='gwsforecast',
            name='forec_et',
            field=models.ForeignKey(related_name='forec_et', default=None, to='data.Series'),
        ),
        migrations.AlterField(
            model_name='gwsforecast',
            name='forec_pt',
            field=models.ForeignKey(related_name='forec_pt', default=None, to='data.Series'),
        ),
        migrations.AlterField(
            model_name='gwsforecast',
            name='forec_tmp',
            field=models.ForeignKey(related_name='forec_tmp', default=None, to='data.Series'),
        ),
        migrations.AlterField(
            model_name='gwsforecast',
            name='hist_ev',
            field=models.ForeignKey(related_name='hist_ev', default=None, to='data.Series'),
        ),
        migrations.AlterField(
            model_name='gwsforecast',
            name='hist_pt',
            field=models.ForeignKey(related_name='hist_pt', default=None, to='data.Series'),
        ),
    ]
