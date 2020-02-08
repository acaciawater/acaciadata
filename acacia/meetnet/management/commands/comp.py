import logging
from django.core.management.base import BaseCommand
from django.db.models import Q
from acacia.meetnet import util
from acacia.meetnet.models import Screen
from django.contrib.auth.models import User
from acacia.data.models import Series

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = ''
    help = 'Maak (gecompenseerde) reeksen'

    def add_arguments(self, parser):
        parser.add_argument('-s', '--screen', type=str, dest='screen')
        parser.add_argument('-r', '--reset', action='store_true', default=False, dest='reset',help='Tijdreeksen opnieuw aanmaken (reset)')
        
    def handle(self, *args, **options):
        user = User.objects.get(username='theo')
        screen_name = options.get('screen')
        reset = options.get('reset')
        known_baros = {}
        wells = set()
        queryset = Screen.objects.all()
        if screen_name:
            well, nr = screen_name.split('/')
            queryset=queryset.filter(Q(well__name__iexact=well)|Q(well__nitg__iexact=well),nr=nr)
        for screen in queryset:
            logger.debug(unicode(screen))
            name = '%s COMP' % screen
            series, created = Series.objects.get_or_create(name=name,defaults={'user':user})
            start = None
            if created:
                logger.debug('Created {}'.format(series))
            elif not reset:
                latest = screen.last_measurement()
                start = latest.date if latest else None

            util.recomp(screen, series, start, known_baros)   
            util.chart_for_screen(screen)
            wells.add(screen.well)
            
        for well in wells:
            util.chart_for_well(well)