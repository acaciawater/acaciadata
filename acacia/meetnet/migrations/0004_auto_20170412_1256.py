# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.core.exceptions import ObjectDoesNotExist

def setlocs(apps, schema_editor):
    Project = apps.get_model('data', 'Project')
    Well = apps.get_model('meetnet', 'Well')
    for w in Well.objects.all():
        net = w.network
        prj = Project.objects.get(name=net.name)
        w.ploc,created = prj.projectlocatie_set.get(name=w.name,defaults={'location': w.location})
        w.save()
        #print 'Well', w.name
        for s in w.screen_set.all():
            name = '%s/%03d' % (w.name, s.nr)
            #print 'Screen', name
            s.mloc,created = w.ploc.meetlocatie_set.get_or_create(name=name,defaults={'location': w.location})
            s.save()
                
class Migration(migrations.Migration):

    dependencies = [
        ('meetnet', '0003_auto_20170412_1255'),
    ]

    operations = [
        migrations.RunPython(setlocs),
    ]
