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
            
#             if hasattr(screen,'handpeilingen') and screen.handpeilingen:
#                 logger.warning('Screen {} skipped: already has Handpeilingen instance'.format(screen))
#                 continue
                
            queryset = ManualSeries.objects.filter(mlocatie=screen.mloc,name__endswith='HAND')
            if not queryset.exists():
                logger.warning('Screen {} skipped: no existing manual measurements found'.format(screen))
                continue

            hand, created = Handpeilingen.objects.get_or_create(screen=screen,defaults = {
                'refpnt': 'bkb',
                'user': user,
                'mlocatie': screen.mloc,
                'name': '{} HAND'.format(screen),
                'unit': 'm',
                'type': 'scatter',
                'timezone': settings.TIME_ZONE})

            if created:
                logger.debug('Created Handpeilingen instance for screen {}'.format(screen))
                ref = 'bkb'
            else:
                ref = hand.refpnt
            
            logger.info('Converting manual series for screen {}'.format(screen))
            for manual in queryset:
                if isinstance(manual, Handpeilingen) or hasattr(manual,'handpeilingen'):
                    continue
                for p in manual.datapoints.all():
                    value = screen.refpnt - p.value if ref == 'bkb'  else p.value
                    h, created=hand.datapoints.update_or_create(date=p.date,defaults = {'value': value})
                    logger.debug('{} {}'.format(h.date, h.value))

            screen.manual_levels = hand
            screen.save(update_fields=('manual_levels',))
            if delete_existing:
                manual.delete()