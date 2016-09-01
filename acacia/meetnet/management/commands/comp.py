'''
Created on Dec 6, 2014

@author: theo
'''
from django.core.management.base import BaseCommand
from acacia.data.models import Series, DataPoint, Chart, MeetLocatie
from acacia.meetnet import util
from acacia.meetnet.models import Well,Screen
from django.contrib.auth.models import User
from django.db.models import F
import math, pytz, datetime

class Command(BaseCommand):
    args = ''
    help = 'Maak luchtdruk gecompenseerde reeksen'
        
    def handle(self, *args, **options):
        user = User.objects.get(username='theo')
        known_baros = {}
        tz = pytz.FixedOffset(60)#Nederlandse wintertijd
        for well in Well.objects.all():
        #for well in Well.objects.exclude(name=F('nitg')):
            for screen in well.screen_set.all():
                print screen
                name = '%s COMP' % screen
                series, created = Series.objects.get_or_create(name=name,defaults={'user':user})
                try:
                    series.mlocatie = MeetLocatie.objects.get(name=unicode(screen))
                    series.save()
                except:
                    pass
                util.recomp(screen, series, known_baros, tz)   
                             
                #maak/update grafiek
                chart, created = Chart.objects.get_or_create(name=unicode(screen), defaults={
                            'title': unicode(screen),
                            'user': user, 
                            'percount': 0, 
                            'start':datetime.datetime(2013,1,1), 
                            'stop': datetime.datetime(2015,12,31),
                            })
                chart.series.get_or_create(series=series, defaults={'label' : 'm tov NAP'})
                # handpeilingen toevoegen (als beschikbaar)
                try:
                    mloc = MeetLocatie.objects.get(name=unicode(screen))
                    for hand in mloc.manualseries_set.all():
                        chart.series.get_or_create(series=hand,defaults={'type':'scatter', 'order': 2})
                except:
                    pass