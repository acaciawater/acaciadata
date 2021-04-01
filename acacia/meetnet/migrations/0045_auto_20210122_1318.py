# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2021-01-22 12:18
from __future__ import unicode_literals

import acacia.meetnet.bro.fields
from django.conf import settings
import django.contrib.gis.db.models.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('meetnet', '0044_auto_20200518_1000'),
    ]

    operations = [
        migrations.CreateModel(
            name='Code',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=40, verbose_name='code')),
            ],
            options={
                'verbose_name': 'Code',
                'verbose_name_plural': 'Codes',
            },
        ),
        migrations.CreateModel(
            name='CodeSpace',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codeSpace', models.CharField(max_length=40, verbose_name='codeSpace')),
                ('description', models.CharField(blank=True, max_length=40, null=True, verbose_name='Description')),
                ('default_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='meetnet.Code', verbose_name='default code')),
            ],
            options={
                'verbose_name': 'Code space',
                'verbose_name_plural': 'Code spaces',
            },
        ),
        migrations.CreateModel(
            name='Defaults',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deliveryAccountableParty', models.CharField(help_text='KVK nummer van de bronhouder', max_length=8, validators=[django.core.validators.RegexValidator(message='Illegal chamber of commerce number', regex=b'\\d{8}')], verbose_name='deliveryAccountableParty')),
                ('owner', models.CharField(help_text=b'KVK-nummer van de eigenaar', max_length=8, validators=[django.core.validators.RegexValidator(message='Illegal chamber of commerce number', regex=b'\\d{8}')], verbose_name='Owner')),
                ('maintenanceResponsibleParty', models.CharField(blank=True, help_text=b'KVK-nummer van de onderhoudende instantie', max_length=8, null=True, validators=[django.core.validators.RegexValidator(message='Illegal chamber of commerce number', regex=b'\\d{8}')], verbose_name='Onderhoudende instantie')),
                ('network', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='bro', to='meetnet.Network', verbose_name='Network')),
            ],
            options={
                'verbose_name': 'Defaults',
                'verbose_name_plural': 'Defaults',
            },
        ),
        migrations.CreateModel(
            name='GroundwaterMonitoringWell',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('objectIdAccountableParty', models.CharField(max_length=100, verbose_name='ObjectID')),
                ('deliveryContext', acacia.meetnet.bro.fields.CodeField(default='publiekeTaak', max_length=20, verbose_name='Kader aanlevering')),
                ('constructionStandard', acacia.meetnet.bro.fields.CodeField(default='onbekend', max_length=20, verbose_name='Kwaliteitsnorm inrichting')),
                ('initialFunction', acacia.meetnet.bro.fields.CodeField(default='stand', max_length=20, verbose_name='Initial function')),
                ('numberOfMonitoringTubes', models.PositiveIntegerField(default=1, verbose_name='Number of monitoring tubes')),
                ('groundLevelStable', acacia.meetnet.bro.fields.IndicationYesNoUnknownEnumeration(max_length=20, verbose_name='Ground level stable')),
                ('wellStability', acacia.meetnet.bro.fields.IndicationYesNoUnknownEnumeration(max_length=20, verbose_name='WellStability')),
                ('nitgCode', models.CharField(blank=True, max_length=8, null=True, verbose_name='NITG code')),
                ('mapSheetCode', models.CharField(blank=True, max_length=3, null=True, verbose_name='Mapsheet')),
                ('owner', models.CharField(help_text='KVK-nummer van de eigenaar', max_length=8, validators=[django.core.validators.RegexValidator(message='Illegal chamber of commerce number', regex=b'\\d{8}')], verbose_name='Owner')),
                ('maintenanceResponsibleParty', models.CharField(blank=True, max_length=8, null=True, validators=[django.core.validators.RegexValidator(message='Illegal chamber of commerce number', regex=b'\\d{8}')], verbose_name='Onderhoudende instantie')),
                ('wellHeadProtector', acacia.meetnet.bro.fields.CodeField(default='onbekend', max_length=20, verbose_name='Beschermconstructie')),
                ('wellConstructionDate', models.DateField(blank=True, null=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326, verbose_name='Coordinaten')),
                ('horizontalPositioningMethod', acacia.meetnet.bro.fields.CodeField(default='RTKGPS2tot5cm', max_length=20, verbose_name='Methode locatiebepaling')),
                ('groundLevelPosition', models.FloatField(verbose_name='Maaiveld')),
                ('groundLevelPositioningMethod', acacia.meetnet.bro.fields.CodeField(default='RTKGPS0tot4cm', max_length=20, verbose_name='Maaiveld positiebepaling')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='modified')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='user')),
                ('well', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='bro', to='meetnet.Well', verbose_name='well')),
            ],
            options={
                'verbose_name': 'GroundwaterMonitoringWell',
                'verbose_name_plural': 'GroundwaterMonitoringWells',
            },
        ),
        migrations.CreateModel(
            name='MapSheet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('area', models.FloatField()),
                ('perimeter', models.FloatField()),
                ('topo_2561_field', models.IntegerField()),
                ('topo_25611', models.IntegerField()),
                ('bladnaam', models.CharField(max_length=20)),
                ('nr', models.IntegerField()),
                ('ltr', models.CharField(max_length=1)),
                ('district', models.CharField(max_length=2)),
                ('blad', models.CharField(max_length=3)),
                ('geom', django.contrib.gis.db.models.fields.PolygonField(srid=28992)),
            ],
        ),
        migrations.CreateModel(
            name='MonitoringTube',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tubeNumber', models.PositiveSmallIntegerField(default=1)),
                ('tubeType', acacia.meetnet.bro.fields.CodeField(default='standaardbuis', max_length=20, verbose_name='Buistype')),
                ('artesianWellCapPresent', acacia.meetnet.bro.fields.IndicationYesNoUnknownEnumeration(max_length=20, verbose_name='ArtesianWellCapPresent')),
                ('sedimentSumpPresent', acacia.meetnet.bro.fields.IndicationYesNoUnknownEnumeration(max_length=20, verbose_name='SedimentSumpPresent')),
                ('numberOfGeoOhmCables', models.PositiveSmallIntegerField(default=0, verbose_name='NumberOfGeoOhmCables')),
                ('tubeTopDiameter', models.FloatField(null=True, verbose_name='Diameter')),
                ('variableDiameter', acacia.meetnet.bro.fields.IndicationYesNoEnumeration(default='nee', max_length=20)),
                ('tubeStatus', acacia.meetnet.bro.fields.CodeField(default='gebruiksklaar', max_length=20, verbose_name='Status')),
                ('tubeTopPosition', models.FloatField(verbose_name='Bovenkant buis')),
                ('tubeTopPositioningMethod', acacia.meetnet.bro.fields.CodeField(default='onbekend', max_length=20, verbose_name='Methode positiebepaling bovenkant buis')),
                ('tubePackingMaterial', acacia.meetnet.bro.fields.CodeField(default='onbekend', max_length=20, verbose_name='Aanvul materiaal')),
                ('tubeMaterial', acacia.meetnet.bro.fields.CodeField(default='pvc', max_length=20, verbose_name='Buismateriaal')),
                ('screenLength', models.FloatField(verbose_name='Filterlengte')),
                ('sockMaterial', acacia.meetnet.bro.fields.CodeField(default='onbekend', max_length=20, verbose_name='Kousmateriaal')),
                ('plainTubePartLength', models.FloatField(verbose_name='Lengte stijgbuis')),
                ('sedimentSump', models.FloatField(default=0, verbose_name='Lengte zandvang')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='modified')),
                ('screen', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='bro', to='meetnet.Screen', verbose_name='tube')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'MonitoringTube',
                'verbose_name_plural': 'MonitoringTubes',
            },
        ),
        migrations.CreateModel(
            name='RegistrationRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requestReference', models.CharField(blank=True, max_length=100, verbose_name='requestReference')),
                ('deliveryAccountableParty', models.CharField(help_text='KVK nummer van bronhouder', max_length=8, validators=[django.core.validators.RegexValidator(message='Illegal chamber of commerce number', regex=b'\\d{8}')], verbose_name='deliveryAccountableParty')),
                ('qualityRegime', acacia.meetnet.bro.fields.CodeField(max_length=20, verbose_name='Kwaliteitsregime')),
                ('underPrivilege', acacia.meetnet.bro.fields.IndicationYesNoEnumeration(default='ja', max_length=20)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='modified')),
                ('gmw', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meetnet.GroundwaterMonitoringWell', verbose_name='GroundwaterMonitoringWell')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'RegistrationRequest',
                'verbose_name_plural': 'RegistrationRequests',
            },
        ),
        migrations.CreateModel(
            name='SourceDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='GMW_Construction',
            fields=[
                ('sourcedocument_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='meetnet.SourceDocument')),
                ('gmw', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meetnet.GroundwaterMonitoringWell')),
            ],
            bases=('meetnet.sourcedocument',),
        ),
        migrations.AddField(
            model_name='code',
            name='codeSpace',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meetnet.CodeSpace'),
        ),
    ]