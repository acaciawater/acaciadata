'''
Created on Feb 13, 2014

@author: theo
'''
from django.core.management.base import BaseCommand
from optparse import make_option
from django.utils.text import slugify
from acacia.data.models import Datasource, Formula
import os,logging
logger = logging.getLogger('acacia.data')

class Command(BaseCommand):
    args = ''
    help = 'Dumps all series as csv files'
    option_list = BaseCommand.option_list + (
            make_option('--dest',
                action='store',
                dest = 'dest',
                default = '.',
                help = 'destination folder'),
            make_option('--pk',
                action='store',
                type = 'int',
                dest = 'pk',
                default = None,
                help = 'dump single datasource'),
        )

    def handle(self, *args, **options):
        dest = options.get('dest', '.')
        pk = options.get('pk', None)
        if pk is None:
            datasources = Datasource.objects.all()
        else:
            datasources = Datasource.objects.filter(pk=pk)
        for d in datasources:
            logger.info('Dumping datasource %s' % d)
            series = d.getseries()
            for s in series:
                logger.info('Series %s' % s.name)
                folder=os.path.join(dest,
                                      slugify(s.datasource().name),
                                      slugify(s.meetlocatie().name))
                if not os.path.exists(folder):
                    os.makedirs(folder)
                filename = os.path.join(folder,slugify(s.name)+'.csv')
                with open(filename,'w') as f:
                    f.write(s.to_csv())
