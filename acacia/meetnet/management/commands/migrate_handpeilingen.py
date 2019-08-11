'''
Created on Aug 11, 2019

@author: theo
'''
from django.core.management.base import BaseCommand
import os,logging
from acacia.data.models import ManualSeries
from acacia.meetnet.models import Screen, Handpeilingen
from django.contrib.auth.models import User
from django.conf import settings
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = ''
    help = 'Migrate manual measurements to Handpeilingen instances'
    
    def add_arguments(self,parser):
        
        parser.add_argument('--pk',
                action='store',
                type = int,
                dest = 'pk',
                default = None,
                help = 'migrate single screen')

        parser.add_argument('--delete',
                action='store_true',
                dest = 'delete',
                default = False,
                help = 'delete existing manual series after successful conversion')

    def handle(self, *args, **options):
        # get the first superuser
        user=User.objects.filter(is_superuser=True).first()
        delete_existing=options['delete']

        pk = options.get('pk', None)
        if pk is None:
            queryset = Screen.objects.order_by('well__name','nr')
        else:
            queryset = Screen.objects.filter(pk=pk)
            
        for screen in queryset:
            
            if hasattr(screen,'handpeilingen') and screen.handpeilingen:
                logger.warning('Screen {} skipped: already has Handpeilingen instance'.format(screen))
                continue
                
            manual = screen.manual_levels or screen.mloc.series_set.filter(name__endswith='HAND').first()
            if manual is None or manual.datapoints.count() == 0:
                logger.warning('Screen {} skipped: no existing manual measurements found'.format(screen))
                continue

            logger.debug('Creating Handpeilingen instance for screen {}'.format(screen))
            hand = Handpeilingen.objects.create(screen=screen,refpnt='bkb',
                                                user=user,
                                                mlocatie = screen.mloc,
                                                name='{} HAND'.format(screen),
                                                unit='m',
                                                type='scatter',
                                                timezone=settings.TIME_ZONE)

            logger.info('Converting manual series for screen {}'.format(screen))
            for p in manual.datapoints.all():
                h=hand.datapoints.create(date=p.date,value=screen.refpnt - p.value)
                logger.debug('{} {}'.format(h.date, h.value))
            screen.manual_levels = hand
            screen.save(update_fields=('manual_levels',))
            if delete_existing:
                manual.delete()