'''
Created on Nov 23, 2016

@author: theo
'''
from django.core.management.base import BaseCommand
#from optparse import make_option
from acacia.data.models import KeyFigure
from acacia.data.loggers import SourceAdapter
import logging

class Command(BaseCommand):
    args = ''
    help = 'Update keyfigures'

    def handle(self, *args, **options):
        with SourceAdapter(logging.getLogger('update')) as logger:
            logger.datasource = ''
            logger.info('***UPDATE OF KEYFIGURES STARTED***')
            for k in KeyFigure.objects.all():
                oldvalue = float(k.value)
                newvalue = float(k.update())
                if oldvalue != newvalue:
                    logger.debug('Keyfigure {loc}: {name} updated to {value}'.format(name=k.name,loc=k.locatie,value=newvalue))
                else:
                    logger.debug('Keyfigure {loc}: {name} not changed'.format(name=k.name,loc=k.locatie))
            logger.info('***UPDATE OF KEYFIGURES COMPLETED***')