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
                help = 'skip update of calculated series')
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
        for d in datasources:
            start = d.stop()
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
                    if pk is None:
                        continue
                    newfiles = None
            else:
                newfilecount = 0
                newfiles = None

            count = count + 1
            if newfilecount == 0:
                self.stdout.write('Reading all files in datasource %s\n' % d.name)
            else:
                self.stdout.write('Reading %s new files in datasource %s\n' % (newfilecount, d.name))
            data = d.get_data(start=start,files=newfiles)
            if data is None:
                # don't bother to continue: no data
                continue
            self.stdout.write('  Updating parameters\n')
            try:
                d.update_parameters(data=data,files=newfiles)
            except Exception as e:
                self.stderr.write('ERROR updating parameters for datasource %s: %s\n' % (d.name, e))
            for p in d.parameter_set.all():
                for s in p.series_set.all():
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
                            