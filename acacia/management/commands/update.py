'''
Created on Feb 13, 2014

@author: theo
'''
from django.core.management.base import BaseCommand
from acacia.data.models import DataFile, Series

class Command(BaseCommand):
    args = ''
    help = 'Downloads data from remote sites and updates time series'

    def handle(self, *args, **options):
        self.stdout.write('Downloading data and updating time series\n')
        count = 0        
        for d in DataFile.objects.exclude(url=None):
            self.stdout.write('Downloading file %s\n' % d.name)
            d.download()
            count = count + 1
            d.update_parameters()
            self.stdout.write('Reading datafile %s\n' % d.file.name)
            data = d.get_data()
            for p in d.parameter_set.all():
                self.stdout.write('  Updating parameter %s\n' % p.name)
                p.make_thumbnail(data=data)
                p.save()
                for s in Series.objects.filter(parameter=p):
                    try:
                        self.stdout.write('    Updating timeseries %s\n' % s.name)
                        s.update()
                        s.make_thumbnail()
                        s.save()
                    except Exception as e:
                        self.stdout.write('***ERROR***Updating timeseries %s: %s\n' % (s.name, e))
        self.stdout.write('%d datafiles updated' % count)