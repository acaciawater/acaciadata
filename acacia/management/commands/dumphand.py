'''
Created on Apr 26, 2019

@author: theo
'''

from django.core.management.base import BaseCommand
from acacia.meetnet.models import Screen
import pytz

class Command(BaseCommand):
    args = ''
    help = 'exporteer handpeilingen'
        
    def handle(self, *args, **options):
        print('NITG,Filter,Datum,Tijd,Meting')
        CET=pytz.timezone('Etc/GMT-1')
        print('Naam,Filter,Datum,Wintertijd,Meting') 
        for screen in Screen.objects.all():
            bkb = screen.refpnt
            series = screen.mloc.series_set.filter(name__endswith='HAND').first()
            if series:
                for p in series.datapoints.order_by('date'):
                    dt = p.date.astimezone(CET)
                    print(','.join(map(str,[screen.well.name, screen.nr, dt.date(), dt.time(), bkb - p.value]))) 