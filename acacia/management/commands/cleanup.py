'''
Created on Feb 13, 2014

@author: theo
'''
import os
from django.core.management.base import BaseCommand, CommandError
from acacia.data.models import Datasource, Parameter, Series
from acacia import settings

class Command(BaseCommand):
    args = ''
    help = 'Deletes unused datafiles and thumbnails from upload area'

    def handle(self, *args, **options):
        # get all files in use
        inuse = [f.filepath() for ds in Datasource.objects.all() for f in ds.sourcefiles]
        inuse.extend([p.thumbpath() for p in Parameter.objects.all()])
        inuse.extend([s.thumbpath() for s in Series.objects.all()])

        self.stdout.write('Checking sourcefiles\n')        
        count = 0
        for path, folders, files in os.walk(os.path.join(settings.MEDIA_ROOT,settings.UPLOAD_DATAFILES)):
            for f in files:
                name = os.path.join(path,f)
                if not name in inuse:
                    self.stdout.write('Deleting %s\n' % name)
                    os.remove(name)
                    count = count+1 
                else:
                    self.stdout.write('Keeping %s\n' % name)
                    
        self.stdout.write('%d datafiles deleted\n' % count)

        self.stdout.write('Checking thumbnails\n')        
        count = 0
        for path, folders, files in os.walk(os.path.join(settings.MEDIA_ROOT,settings.UPLOAD_THUMBNAILS)):
            for f in files:
                name = os.path.join(path,f)
                if not name in inuse:
                    self.stdout.write('Deleting %s\n' % name) 
                    os.remove(name)
                    count = count+1
                else:
                    self.stdout.write('Keeping %s\n' % name)
        self.stdout.write('%d thumbnails deleted\n' % count)
