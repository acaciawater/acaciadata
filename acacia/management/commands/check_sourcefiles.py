'''
Created on Feb 13, 2014

@author: theo
'''
from django.core.management.base import BaseCommand
from acacia.data.models import SourceFile
from optparse import make_option
import os

class Command(BaseCommand):
    args = ''
    help = 'Checks existence of sourcefiles'
    option_list = BaseCommand.option_list + (
        make_option('--delete',
            action='store_true',
            dest='delete',
            default=False,
            help='Delete source files that do not exist'),
        )
    def handle(self, *args, **options):
        should_delete = options.get('delete')
        files = SourceFile.objects.all()
        count = files.count()
        if count == 0:
            self.stdout.write('No source files found\n')
            return
        self.stdout.write('Checking %d sourcefiles\n' % count)
        notexist = 0
        notreadable = 0
        notdefined=0
        deleted = 0
        for f in files:
            if not hasattr(f,'file'):
                self.stdout.write('%s has no file attribute' % f)
                if should_delete:
                    f.delete()
                    deleted += 1
                notdefined += 1
                continue
            try:
                path = f.file.path
            except Exception as e:
                self.stdout.write('%s has no file associated with it' % f)
                if should_delete:
                    f.delete()
                    deleted += 1
                notdefined += 1
                continue
            if not os.path.isfile(path):
                self.stdout.write('%s does not exist' % path)
                if should_delete:
                    f.delete()
                    deleted += 1
                notexist += 1
            elif not os.access(path, os.R_OK):
                self.stdout.write('%s exists but is not readable' % path)
                notreadable += 1
        self.stdout.write('%d files were not found' % notexist)
        self.stdout.write('%d files could not be read' % notreadable)
        self.stdout.write('%d files were not defined' % notdefined)
        self.stdout.write('%d files were deleted' % deleted)
