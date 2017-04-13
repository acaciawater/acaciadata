'''
Created on Apr 13, 2017

@author: theo
'''
from django.core.management.base import BaseCommand
from acacia.data.models import Datasource
import logging
from acacia.data.loggers import SourceAdapter
from acacia.data.models import Generator
from acacia.meetnet.actions import make_wellcharts
 
class Command(BaseCommand):
    args = ''
    help = 'Updates Ellitrack charts'
    
    def add_arguments(self, parser):
        parser.add_argument('--pk',
                action='store',
                type = int,
                dest = 'pk',
                default = None,
                help = 'update single datasource')

    def handle(self, *args, **options):
        with SourceAdapter(logging.getLogger(__name__)) as logger:
            logger.source = ''
            logger.info('***UPDATE ELLITRACK CHARTS***')
            count = 0
            elli = Generator.objects.get(name='Ellitrack')
            pk = options.get('pk', None)
            if pk is None:
                datasources = Datasource.objects.filter(generator=elli)
            else:
                datasources = Datasource.objects.filter(pk=pk)
            # find wells with Ellitrack logger
            selected = [ds.loggerdatasource.logger for ds in datasources if hasattr(ds,'loggerdatasource')]
            loggers = [lg for lg in selected if lg.model.startswith('etd')]
            wells = [pos.screen.well for lgr in loggers for pos in lgr.loggerpos_set.all()]
            make_wellcharts(None,None,wells)
            logger.info('***UPDATE ELLITRACK CHARTS COMPLETED***')
