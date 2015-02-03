'''
Created on Feb 13, 2014

@author: theo
'''
from django.core.management.base import BaseCommand
from optparse import make_option
from acacia.data.models import Datasource, Formula
import logging
from acacia.data.loggers import DatasourceAdapter

logger = DatasourceAdapter(logging.getLogger('update'))

class Command(BaseCommand):
    args = ''
    help = 'Downloads data from remote sites and updates time series'
    option_list = BaseCommand.option_list + (
            make_option('--nodownload',
                action='store_false',
                dest='down',
                default=True,
                help='Don\'t download new files'),
            make_option('--pk',
                action='store',
                type = 'int',
                dest = 'pk',
                default = None,
                help = 'update single datasource'),
            make_option('--nocalc',
                action='store_false',
                dest = 'calc',
                default = True,
                help = 'skip update of calculated series'),
            make_option('--replace',
                action='store_true',
                dest = 'replace',
                default = False,
                help = 'recreate existing series')
        )
    def handle(self, *args, **options):
        down = options.get('down')
        logger.datasource = ''
        if down:
            logger.info('Downloading data, updating parameters and related time series')
        else:
            logger.info('Updating parameters and related time series')
        count = 0
        pk = options.get('pk', None)
        if pk is None:
            datasources = Datasource.objects.all()
        else:
            datasources = Datasource.objects.filter(pk=pk)

        replace = options.get('replace')
        if replace:
            logger.info('Recreating series')
        
        for d in datasources:
            logger.datasource = d
            logger.info('Updating datasource %s', d.name)
            if not d.autoupdate and pk is None:
                continue
            try:
                series = d.getseries()
                if replace:
                    start = None
                else:
                    # actualiseren (data toevoegen) vanaf laatste punt
                    data_start = d.stop()
                    if len(series) == 0:
                        series_start = data_start
                    else:
                        # actialisatie vanaf een na laatste datapoint
                        # (rekening houden met niet volledig gevulde laatste tijdsinterval bij accumulatie of sommatie)
                        series_start = min([p.date for p in [s.beforelast() for s in series] if p is not None])
                    if data_start is None:
                        start = series_start
                    else:
                        start = min(series_start,data_start)
    
                if down and d.autoupdate and d.url is not None:
                    logger.info('Downloading datasource %s' % d.name)
                    try:
                        newfiles = d.download()
                    except Exception as e:
                        logger.error('ERROR downloading datasource %s: %s' % (d.name, e))
                        continue
                    if newfiles is None:
                        newfilecount = 0
                    else:
                        newfilecount = len(newfiles)
                    logger.info('Got %d new files' % newfilecount)
                    if newfilecount == 0:
                        newfiles = None
                else:
                    newfilecount = 0
                    newfiles = None
    
                count = count + 1
                logger.info('Reading datasource %s' % d.name)
                try:
                    data = d.get_data(start=start)
                except Exception as e:
                    logger.error('Error reading datasource %s: %s', d.name, e)
                    continue
                if data is None:
                    # don't bother to continue: no data
                    continue
                logger.info('Updating parameters')
                try:
                    d.update_parameters(data=data,files=newfiles,limit=10)
                    if replace:
                        d.make_thumbnails(data=data)
                except Exception as e:
                    logger.error('ERROR updating parameters for datasource %s: %s' % (d.name, e))
                for s in series:
                    logger.info('Updating timeseries %s' % s.name)
                    try:
                        if replace:
                            s.replace()
                        else:
                            s.update(data,start=start)
                    except Exception as e:
                        logger.error('ERROR updating timeseries %s: %s' % (s.name, e))
            except Exception as e:
                logger.error('ERROR updating datasource %s: %s' % (d.name, e))

        logger.datasource = ''
        logger.info('%d datasources were updated' % count)
        
        if Formula.objects.count() > 0:
            calc = options.get('calc')
            if calc:
                logger.info('Updating calculated timeseries')
                count = 0
                # TODO: sort formulas by dependency
                for f in Formula.objects.all():
                    logger.info('Updating timeseries %s' % f.name)
                    try:
                        f.update()
                        count = count + 1
                    except Exception as e:
                        logger.error('ERROR updating calculated timeseries %s: %s' % (f.name, e))
                logger.info('%d calculated timeseries were updated' % count)
                            