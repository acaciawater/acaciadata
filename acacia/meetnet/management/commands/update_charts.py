'''
Created on Apr 13, 2017

@author: theo
'''
from django.core.management.base import BaseCommand
import logging
from acacia.data.loggers import SourceAdapter
from acacia.meetnet.actions import make_wellcharts
from acacia.meetnet.models import Well
 
class Command(BaseCommand):
    args = ''
    help = 'Updates Ellitrack charts'
    
    def add_arguments(self, parser):
        parser.add_argument('--pk',
                action='store',
                type = int,
                dest = 'pk',
                default = None,
                help = 'update chart of single well')

    def handle(self, *args, **options):
        with SourceAdapter(logging.getLogger(__name__)) as logger:
            logger.source = ''
            logger.info('***UPDATE ELLITRACK CHARTS***')
            pk = options.get('pk', None)
            if pk:
                wells = Well.objects.filter(pk=pk)
            else:
                # get all wells with ellitrack loggers
                wells = Well.objects.filter(screen__loggerpos__logger__model__istartswith='etd').distinct()
            make_wellcharts(None,None,wells)
            logger.info('***UPDATE ELLITRACK CHARTS COMPLETED***')
