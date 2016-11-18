# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0014_auto_20161117_1324'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='plotband',
            options={'verbose_name': 'Strook', 'verbose_name_plural': 'Stroken'},
        ),
        migrations.AlterModelOptions(
            name='plotline',
            options={'verbose_name': 'Lijn', 'verbose_name_plural': 'Lijnen'},
        ),
        migrations.AddField(
            model_name='plotband',
            name='orientation',
            field=models.CharField(default='v', max_length=1, verbose_name=b'ori\xc3\xabntatie', choices=[(b'h', b'horizontaal'), (b'v', b'vertikaal')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='plotline',
            name='orientation',
            field=models.CharField(default='v', max_length=1, verbose_name=b'ori\xc3\xabntatie', choices=[(b'h', b'horizontaal'), (b'v', b'vertikaal')]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='bandstyle',
            name='borderColor',
            field=models.CharField(default=b'black', max_length=32, verbose_name=b'randkleur'),
        ),
        migrations.AlterField(
            model_name='bandstyle',
            name='borderwidth',
            field=models.IntegerField(default=0, verbose_name=b'breedte rand'),
        ),
        migrations.AlterField(
            model_name='bandstyle',
            name='fillcolor',
            field=models.CharField(max_length=32, verbose_name=b'achtergrondkleur'),
        ),
        migrations.AlterField(
            model_name='bandstyle',
            name='fillstyle',
            field=models.CharField(default=b'solid', max_length=32, verbose_name=b'arcering'),
        ),
        migrations.AlterField(
            model_name='bandstyle',
            name='name',
            field=models.CharField(max_length=32, verbose_name=b'naam'),
        ),
        migrations.AlterField(
            model_name='bandstyle',
            name='opacity',
            field=models.FloatField(default=0.8, verbose_name=b'transparantie'),
        ),
        migrations.AlterField(
            model_name='bandstyle',
            name='zIndex',
            field=models.IntegerField(default=0, verbose_name=b'volgorde'),
        ),
        migrations.AlterField(
            model_name='linestyle',
            name='color',
            field=models.CharField(default=b'black', max_length=32, verbose_name=b'kleur'),
        ),
        migrations.AlterField(
            model_name='linestyle',
            name='dashStyle',
            field=models.CharField(default=b'Solid', max_length=32, verbose_name=b'stijl', choices=[(b'Solid', b'Standaard'), (b'Dash', b'Gestreept'), (b'Dot', b'Gestippeld')]),
        ),
        migrations.AlterField(
            model_name='linestyle',
            name='name',
            field=models.CharField(max_length=32, verbose_name=b'naam'),
        ),
        migrations.AlterField(
            model_name='linestyle',
            name='opacity',
            field=models.FloatField(default=0.8, verbose_name=b'transparantie'),
        ),
        migrations.AlterField(
            model_name='linestyle',
            name='width',
            field=models.CharField(default=b'0', max_length=32, verbose_name=b'breedte'),
        ),
        migrations.AlterField(
            model_name='linestyle',
            name='zIndex',
            field=models.IntegerField(default=0, verbose_name=b'volgorde'),
        ),
        migrations.AlterField(
            model_name='plotband',
            name='chart',
            field=models.ForeignKey(verbose_name=b'grafiek', to='data.Chart'),
        ),
        migrations.AlterField(
            model_name='plotband',
            name='high',
            field=models.CharField(max_length=32, verbose_name=b'tot'),
        ),
        migrations.AlterField(
            model_name='plotband',
            name='low',
            field=models.CharField(max_length=32, verbose_name=b'van'),
        ),
        migrations.AlterField(
            model_name='plotband',
            name='repetition',
            field=models.CharField(max_length=32, verbose_name=b'herhaling'),
        ),
        migrations.AlterField(
            model_name='plotband',
            name='style',
            field=models.ForeignKey(verbose_name=b'stijl', to='data.BandStyle'),
        ),
        migrations.AlterField(
            model_name='plotline',
            name='chart',
            field=models.ForeignKey(verbose_name=b'grafiek', to='data.Chart'),
        ),
        migrations.AlterField(
            model_name='plotline',
            name='repetition',
            field=models.CharField(default=b'0', max_length=32, verbose_name=b'herhaling'),
        ),
        migrations.AlterField(
            model_name='plotline',
            name='style',
            field=models.ForeignKey(verbose_name=b'stijl', to='data.LineStyle'),
        ),
        migrations.AlterField(
            model_name='plotline',
            name='value',
            field=models.CharField(max_length=32, verbose_name=b'waarde'),
        ),
    ]
