'''
Created on Feb 13, 2014

@author: theo
'''
from django.core.management.base import BaseCommand
from acacia.data.models import Datasource, Formula, aware
import logging
from acacia.data.loggers import SourceAdapter
from datetime import datetime
 
class Command(BaseCommand):
    args = ''
    help = 'Downloads data from remote sites and updates time series'
    
    def add_arguments(self, parser):
        parser.add_argument('-d','--nodownload',
                action='store_false',
                dest='down',
                default=True,
                help='Don\'t download new files')
        parser.add_argument('--pk',
                action='store',
                type = int,
                dest = 'pk',
                default = None,
                help = 'update single datasource')
        parser.add_argument('-c', '--nocalc',
                action='store_false',
                dest = 'calc',
                default = True,
                help = 'skip update of calculated series')
        parser.add_argument('--replace',
                action='store_true',
                dest = 'replace',
                default = False,
                help = 'recreate existing series')
        parser.add_argument('--nothumb',
                action='store_false',
                dest = 'thumb',
                default = True,
                help = 'don\'t update thumbnails for series'),
        parser.add_argument('-f','--force',
                action='store_true',
                dest = 'force',
                default = False,
                help = 'force update of timeseries')

    def handle(self, *args, **options):
        with SourceAdapter(logging.getLogger(__name__)) as logger:
            logger.source = ''
            logger.info('***UPDATE STARTED***')
            thumb = options.get('thumb')
            down = options.get('down')
            force = options.get('force')

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
            
            # remember which series have changed during update
            changed_series = []
            
            for d in datasources:
                if not d.autoupdate and pk is None:
                    continue
                logger.source = d
                logger.info('Updating datasource %s' % d.name)
                try:
                    series = d.getseries()
                    if replace:
                        start = None
                    else:
                        # actualiseren (data toevoegen) vanaf laatste punt
                        # set starting date/time for update as last date/time in current sourcefiles
                        data_stop = d.stop()
                        if len(series) == 0:
                            last = {}
                        else:
                            # maak dict met een na laatste datapoint per tijdreeks
                            # (rekening houden met niet volledig gevulde laatste tijdsinterval bij accumulatie of sommatie)
                            last = {s: s.beforelast().date for s in series if s.aantal() > 0}
                                
                    if down and d.autoupdate:
                        logger.info('Downloading datasource')
                        try:
                            # if start is in the future, use datetime.now as start to overwrite previous forecasts
                            start = min(data_stop, aware(datetime.now()))
                            newfiles = d.download(start)
                        except Exception as e:
                            logger.exception('ERROR downloading datasource: %s' % e)
                            newfiles = None
                        newfilecount = len(newfiles) if newfiles else 0
                        logger.info('Got %d new files' % newfilecount)

                    # for update use newfiles AND the existing sourcefiles that contain data for aggregation
                    if last:
                        after = min(last.values())
                        candidates = d.sourcefiles.filter(stop__gte=after)
                    else:
                        after = None
                        candidates = d.sourcefiles.all()
                    if not candidates:
                        logger.warning('No new data for datasource {ds}'.format(ds=d))
                        if not force:
                            logger.debug('Update of timeseries skipped')
                            continue
                    else:
                        count += 1
                        
                    logger.info('Reading datasource')
                    try:
                        data = d.get_data(files=candidates,start=after)
                    except Exception as e:
                        logger.exception('Error reading datasource: %s', e)
                        continue
                    if data is None:
                        logger.error('No new data for datasource {ds}'.format(ds=d))
                        # don't bother to continue: no data
                        continue
                    if replace:
                        logger.info('Updating parameters')
                        try:
                            d.update_parameters(data=data,files=candidates,limit=10)
                            if replace:
                                d.make_thumbnails(data=data)
                        except Exception as e:
                            logger.exception('ERROR updating parameters for datasource: %s' % e)

                    updated = 0
                    for s in series:
                        logger.info('Updating timeseries %s' % s.name)
                        try:
                            # replace timeseries or update after beforelast datapoint
                            start = last.get(s,None)
                            changes = s.replace(data) if replace else s.update(data,start=start,thumbnail=thumb) 
                            if changes:
                                updated += 1
                                logger.debug('%d datapoints updated for %s' % (changes, s.name))    
                                changed_series.append(s)
                            else:
                                logger.warning('No updates for %s' % s.name)    
                        except Exception as e:
                            logger.exception('ERROR updating timeseries %s: %s' % (s.name, e))
                
                    if updated:
                        logger.info('{} time series updated for datasource {}'.format(updated,d.name))
                
                except Exception as e:
                    logger.exception('ERROR updating datasource %s: %s' % (d.name, e))
                
            logger.source = ''
            logger.info('%d datasources were updated' % count)

            calc = options.get('calc',True)
            if calc:

                def update_formula(f):
                    
                    count = 0
                    
                    # update dependent formulas first
                    for d in f.get_dependencies():
                        if d in formulas:
                            count += update_formula(d)
                    try:
                        logger.info('Updating calculated time series %s' % f.name)
                        if f.update(thumbnail=False) == 0:
                            logger.warning('No new data for %s' % f.name)
                        count += 1
                    except Exception as e:
                        logger.exception('ERROR updating calculated time series %s: %s' % (f.name, e))
                    formulas.remove(f)
                    return count
                
                # get all unique formulas to update
                formulas = set()
                for f in Formula.objects.all():
                    for d in f.get_dependencies():
                        if d in changed_series:
                            formulas.add(f)
                            break
                        
                formulas = list(formulas)
                count = 0
                while formulas:
                    count += update_formula(formulas[0])
                    
                logger.info('%d calculated time series were updated' % count)

            logger.info('***UPDATE COMPLETED***')
                    