'''
Created on Feb 13, 2014

@author: theo
'''
import os, re
from django.core.management.base import BaseCommand, CommandError
from acacia.data.models import Project, ProjectLocatie, MeetLocatie, Datasource, Parameter, Series
from django.conf import settings

class Command(BaseCommand):
    args = ''
    help = 'Deletes unused files from upload area'
    
    def add_arguments(self, parser):
        parser.add_argument('-a','--all',
                action='store_true',
                dest='all',
                default=False,
                help='Check ALL files in media folder')
        parser.add_argument('-n','--no-delete',
                action='store_true',
                dest='dry',
                default=False,
                help="Dry run: don't delete the files")

    def process_folder(self,folder,inuse,dry,verbose):
        count = 0
        bytes = 0
        for path, folders, files in os.walk(folder):
            for f in files:
                name = os.path.join(path,f)
                if not name in inuse:
                    self.stdout.write('Deleting %s\n' % name)
                    try:
                        size = os.path.getsize(name)
                        if not dry:
                            os.remove(name)
                        count = count+1
                        bytes += size 
                    except Exception as e:
                        self.stdout.write('Error deleting %s: %s\n' % (name,e))
                else:
                    if verbose:
                        self.stdout.write('Keeping %s\n' % name)
                    pass
        return (count, bytes)
                
    def handle(self, *args, **options):
        # get all files in use
        verbosity = int(options.get('verbosity',0))
        alles = options.get('all')
        inuse = [f.filepath() for ds in Datasource.objects.all() for f in ds.sourcefiles.all()]
        if alles:
            inuse.extend([p.image.path for p in Project.objects.exclude(image='')])
            inuse.extend([l.image.path for l in ProjectLocatie.objects.exclude(image='')])
            inuse.extend([m.image.path for m in MeetLocatie.objects.exclude(image='')])
            inuse.extend([p.thumbpath() for p in Parameter.objects.exclude(thumbnail='')])
            inuse.extend([s.thumbpath() for s in Series.objects.exclude(thumbnail='')])
        
        if alles:
            roots = [settings.MEDIA_ROOT]
        else:
            # check only datafolders
            pattern = '/'+settings.UPLOAD_DATAFILES + '/'
            roots = set()
            lenpat = len(pattern)
            for pathname in inuse:
                dirname = os.path.dirname(pathname)
                pos = dirname.find(pattern)
                if pos:
                    dirname = dirname[:pos+lenpat]
                roots.add(dirname)

        count = 0
        bytes = 0
        dry = options.get('dry')
        for folder in roots:
            c,b = self.process_folder(folder, inuse, dry, verbosity)
            count += c
            bytes += b
        self.stdout.write('{} files deleted ({} Mb)\n'.format(count, bytes / (1024*1024)))
        