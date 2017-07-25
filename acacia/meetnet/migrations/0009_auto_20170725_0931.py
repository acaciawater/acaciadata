# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0022_merge'),
        ('meetnet', '0008_auto_20170524_1510'),
    ]

    operations = [
        migrations.CreateModel(
            name='MeteoData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('baro', models.ForeignKey(related_name='well_baro', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='data.Series', null=True)),
                ('neerslag', models.ForeignKey(related_name='well_p', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='data.Series', null=True)),
                ('temperatuur', models.ForeignKey(related_name='well_temp', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='data.Series', null=True)),
                ('verdamping', models.ForeignKey(related_name='well_ev24', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='data.Series', null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='loggerpos',
            name='baro',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='data.Series', help_text=b'tijdreeks voor luchtdruk compensatie', null=True, verbose_name=b'luchtdruk'),
        ),
        migrations.AlterField(
            model_name='well',
            name='baro',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='data.Series', help_text=b'tijdreeks voor luchtdruk compensatie', null=True, verbose_name=b'luchtdruk'),
        ),
        migrations.AddField(
            model_name='meteodata',
            name='well',
            field=models.OneToOneField(related_name='meteo', to='meetnet.Well'),
        ),
    ]
