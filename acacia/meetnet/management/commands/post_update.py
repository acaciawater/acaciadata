import logging

from django.core.management.base import BaseCommand

from acacia.meetnet.models import Screen
from acacia.meetnet.actions import make_wellcharts
from django.contrib.auth.models import User
from acacia.meetnet.util import register_screen, recomp
from acacia.data.models import Generator

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Perform required actions after update of datasources and series (acacia.data)'
    
    def handle(self, *args, **options):
        # get admin user
        user = User.objects.filter(is_superuser=True).first()
        
        # dict with airpressure
        baros = {}

        # set of well to update
        wells = set()
                
        logger.info('Updating time series')
        
        generators = Generator.objects.filter(name__in=['Ellitrack','Bliksensing'])
        screens = Screen.objects.filter(loggerpos__logger__datasources__generator__in=generators)
        for screen in screens:
        
            logger.info(screen)
            register_screen(screen)
            
            # get or create compensated series
            name = '%s COMP' % unicode(screen)
            series, created = screen.mloc.series_set.get_or_create(name=name,defaults={
                'user': user,
                'timezone': 'UTC'
            })
            if created:
                logger.debug('Created timeseries {}'.format(series))

            last = screen.last_measurement()
            start = last.date if last else None

            # update set of source files
            new_files = 0
            for lp in screen.loggerpos_set.filter(logger__datasources__generator__in=generators):
                new_files += lp.update_files()
            
            if new_files>0:
                old_count = series.aantal()
                inserted = recomp(screen, series, start, baros)
                new_count = series.aantal()
                logger.debug('{} data points added to timeseries {}'.format(new_count - old_count, series))
                if inserted > 0:
                    wells.add(screen.well)
                
        make_wellcharts(None,None,wells)
        