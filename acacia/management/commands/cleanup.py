'''
Created on Feb 13, 2014

@author: theo
'''
import os
from django.core.management.base import BaseCommand, CommandError
from acacia.data.models import Project, ProjectLocatie, MeetLocatie, Datasource, Parameter, Series
from django.conf import settings

class Command(BaseCommand):
    args = ''
    help = 'Deletes unused files from upload area'

    def handle(self, *args, **options):
        # get all files in use
        inuse = ([p.image.path for p in Project.objects.exclude(image='')])
        inuse.extend([l.image.path for l in ProjectLocatie.objects.exclude(image='')])
        inuse.extend([m.image.path for m in MeetLocatie.objects.exclude(image='')])
        inuse.extend([f.filepath() for ds in Datasource.objects.all() for f in ds.sourcefiles.all()])
        inuse.extend([p.thumbpath() for p in Parameter.objects.exclude(thumbnail='')])
        inuse.extend([s.thumbpath() for s in Series.objects.exclude(thumbnail='')])

        count = 0
        for path, folders, files in os.walk(settings.MEDIA_ROOT):
            for f in files:
                name = os.path.join(path,f)
                if not name in inuse:
                    self.stdout.write('Deleting %s\n' % name)
                    os.remove(name)
                    count = count+1 
                else:
                    #self.stdout.write('Keeping %s\n' % name)
                    pass
                    
        self.stdout.write('%d files deleted\n' % count)
