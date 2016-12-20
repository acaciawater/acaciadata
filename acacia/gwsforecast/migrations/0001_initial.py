# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0007_auto_20161117_1106'),
    ]

    operations = [
        migrations.CreateModel(
            name='GWSForecast',
            fields=[
                ('datasource_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='data.Datasource')),
                ('forec_et', models.ForeignKey(related_name='forec_et', blank=True, to='data.Series', null=True)),
                ('forec_pt', models.ForeignKey(related_name='forec_pt', blank=True, to='data.Series', null=True)),
                ('forec_tmp', models.ForeignKey(related_name='forec_tmp', blank=True, to='data.Series', null=True)),
                ('hist_ev', models.ForeignKey(related_name='hist_ev', blank=True, to='data.Series', null=True)),
                ('hist_gws', models.ForeignKey(to='data.Series')),
                ('hist_pt', models.ForeignKey(related_name='hist_pt', blank=True, to='data.Series', null=True)),
            ],
            bases=('data.datasource',),
        ),
    ]
