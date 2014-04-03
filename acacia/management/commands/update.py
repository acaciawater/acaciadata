'''
Created on Feb 13, 2014

@author: theo
'''
from django.core.management.base import BaseCommand
from optparse import make_option
from acacia.data.models import Datasource, Series

class Command(BaseCommand):
    args = ''
    help = 'Downloads data from remote sites and updates time series'
    def handle(self, *args, **options):
        self.stdout.write('Downloading data and updating time series\n')
        count = 0
        datasources = Datasource.objects.exclude(url=None)         
        for d in datasources:
            self.stdout.write('Downloading datasource %s\n' % d.name)
            newfilecount = d.download()
            self.stdout.write('Got %d new files\n' % newfilecount)
            if newfilecount == 0:
                continue
            count = count + 1
            self.stdout.write('Reading datasource %s\n' % d.name)
            data = d.get_data()
            self.stdout.write('  Updating parameters\n')
            d.update_parameters(data)
            for p in d.parameter_set.all():
                for s in p.series_set.all():
                    self.stdout.write('  Updating timeseries %s\n' % s.name)
                    s.update(data)
        self.stdout.write('%d datasources updated' % count)