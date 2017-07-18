# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('validation', '0009_baserule_polymorphic_ctype'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='baserule',
            options={'verbose_name': 'Validatieregel'},
        ),
        migrations.AlterModelOptions(
            name='diffrule',
            options={'verbose_name': 'Lokale uitbijter'},
        ),
        migrations.AlterModelOptions(
            name='nodatarule',
            options={'verbose_name': 'Geen gegevens'},
        ),
        migrations.AlterModelOptions(
            name='outlierrule',
            options={'verbose_name': 'Uitbijter'},
        ),
        migrations.AlterModelOptions(
            name='seriesrule',
            options={'verbose_name': 'Tijdreeks'},
        ),
        migrations.AlterModelOptions(
            name='valuerule',
            options={'verbose_name': 'Vaste grens'},
        ),
        migrations.AddField(
            model_name='diffrule',
            name='tolerance',
            field=models.FloatField(default=3, help_text=b'gemiddelde plus of min x maal de standaardafwijking', verbose_name=b'tolerantie'),
        ),
        migrations.AddField(
            model_name='outlierrule',
            name='tolerance',
            field=models.FloatField(default=3, help_text=b'gemiddelde plus of min x maal de standaardafwijking', verbose_name=b'tolerantie'),
        ),
    ]
