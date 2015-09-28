'''
Created on Feb 13, 2014

@author: theo
'''
from django.core.management.base import BaseCommand
from optparse import make_option
from acacia.data.models import Datasource, Formula
import logging
from acacia.data.loggers import DatasourceAdapter, BufferingEmailHandler

# Move this part to settings.py
# email_handler=BufferingEmailHandler(fromaddr='webmaster@acaciadata.com', subject='Houston, we have a problem', capacity=1000, interval=30)
# email_handler.setFormatter(logging.Formatter('%(levelname)s %(asctime)s %(datasource)s: %(message)s'))
# email_handler.setLevel(logging.DEBUG)
# logging.getLogger('acacia.data').addHandler(email_handler)

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
        with DatasourceAdapter(logging.getLogger('acacia.data')) as logger:
            #logging.getLogger('acacia.data').addHandler(email_handler)
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
            
            # remember which series have changed during update
            changed_series = []
            
            for d in datasources:
                if not d.autoupdate and pk is None:
                    continue
                logger.datasource = d
                logger.info('Updating datasource')
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
                            last = [p.date for p in [s.beforelast() for s in series] if p is not None]
                            if len(last)>0:
                                series_start = min(last)
                            else:
                                series_start = data_start
                                
                        if data_start is None:
                            start = series_start
                        else:
                            start = min(series_start,data_start)
        
                    if down and d.autoupdate and d.url is not None:
                        logger.info('Downloading datasource')
                        try:
                            newfiles = d.download()
                        except Exception as e:
                            logger.exception('ERROR downloading datasource: %s' % e)
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

                    if down and newfilecount == 0:
                        # we tried to download but there is no new data
                        logger.debug('Update of timeseries skipped')
                        continue
                    
                    count = count + 1
                    # TODO: Avoid reading the data twice: d.download() has called sourcefile.save() which reads the data and updates dimensions
                    logger.info('Reading datasource')
                    try:
                        data = d.get_data(files=newfiles,start=start)
                    except Exception as e:
                        logger.exception('Error reading datasource: %s', e)
                        continue
                    if data is None:
                        # don't bother to continue: no data
                        continue
                    if replace:
                        logger.info('Updating parameters')
                        try:
                            d.update_parameters(data=data,files=newfiles,limit=10)
                            if replace:
                                d.make_thumbnails(data=data)
                        except Exception as e:
                            logger.exception('ERROR updating parameters for datasource: %s' % e)

                    for s in series:
                        logger.info('Updating timeseries %s' % s.name)
                        try:
                            changes = s.replace() if replace else s.update(data,start=start) 
                            if changes > 0:
                                changed_series.append(s)
                                
                        except Exception as e:
                            logger.exception('ERROR updating timeseries %s: %s' % (s.name, e))
                
                    logger.info('Datasource updated.')
                
                except Exception as e:
                    logger.exception('ERROR updating datasource %s: %s' % (d.name, e))
                
            logger.datasource = ''
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
                        f.update()
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

            #email_handler.flush()
            #logging.getLogger('acacia.data.update').removeHandler(email_handler)
                    