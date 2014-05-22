'''
Created on Feb 13, 2014

@author: theo
'''
from django.core.management.base import BaseCommand
from acacia.data.models import SourceFile

class Command(BaseCommand):
    args = ''
    help = 'Deletes empty sourcefiles'

    def handle(self, *args, **options):
        files = SourceFile.objects.filter(rows=0)
        count = files.count()
        if count == 0:
            self.stdout.write('No empty files found\n')
        else:
            self.stdout.write('Deleting %d empty files\n' % count)
            files.delete()
