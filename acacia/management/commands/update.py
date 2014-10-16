'''
Created on Feb 13, 2014

@author: theo
'''
from django.core.management.base import BaseCommand
from optparse import make_option
from acacia.data.models import Datasource, Formula

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
        if down:
            self.stdout.write('Downloading data, updating parameters and related time series\n')
        else:
            self.stdout.write('Updating parameters and related time series\n')
        count = 0
        pk = options.get('pk', None)
        if pk is None:
            datasources = Datasource.objects.exclude(autoupdate=False, url=None)
        else:
            datasources = Datasource.objects.filter(pk=pk, autoupdate=True)

        replace = options.get('replace')
        if replace:
            self.stdout.write('Recreating all series\n')
        
        for d in datasources:
            series = d.getseries()
            if replace:
                start = None
            else:
                data_start = d.stop()
                if len(series) == 0:
                    series_start = data_start
                else:
                    series_start = min([s.tot() for s in series])
                start = min(series_start,data_start)

            if down:
                self.stdout.write('Downloading datasource %s\n' % d.name)
                try:
                    newfiles = d.download()
                except Exception as e:
                    self.stderr.write('ERROR downloading datasource %s: %s\n' % (d.name, e))
                    continue
                newfilecount = len(newfiles)
                self.stdout.write('Got %d new files\n' % newfilecount)
                if newfilecount == 0:
                    newfiles = None
            else:
                newfilecount = 0
                newfiles = None

            count = count + 1
            self.stdout.write('Reading datasource %s\n' % d.name)
            data = d.get_data(start=start)
            if data is None:
                # don't bother to continue: no data
                continue
            self.stdout.write('  Updating parameters\n')
            try:
                d.update_parameters(data=data,files=newfiles,limit=10)
            except Exception as e:
                self.stderr.write('ERROR updating parameters for datasource %s: %s\n' % (d.name, e))
            for s in series:
                self.stdout.write('  Updating timeseries %s\n' % s.name)
                try:
                    s.update(data)
                except Exception as e:
                    self.stderr.write('ERROR updating timeseries %s: %s\n' % (s.name, e))
        self.stdout.write('%d datasources were updated\n' % count)
        
        if Formula.objects.count() > 0:
            calc = options.get('calc')
            if calc:
                self.stdout.write('Updating calculated timeseries\n')
                count = 0
                for f in Formula.objects.all():
                    self.stdout.write('  Updating timeseries %s\n' % f.name)
                    try:
                        f.update()
                        count = count + 1
                    except Exception as e:
                        self.stderr.write('ERROR updating calculated timeseries %s: %s\n' % (f.name, e))
                self.stdout.write('%d calculated timeseries were updated\n' % count)
                            