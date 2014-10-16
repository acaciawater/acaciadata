'''
Created on Oct 9, 2014

@author: theo
'''

import os
from django.core.management.base import BaseCommand, CommandError
from acacia.data.models import DataPoint, SourceFile
from acacia import settings
from django.utils import timezone

def make_aware(d,tz=timezone.UTC):
    if d is not None:
        if timezone.is_naive(d):
            return (True, timezone.make_aware(d, tz))
    return (False, d)

def make_naive(d):
    if d is not None:
        if timezone.is_aware(d):
            return (True, timezone.make_naive(d))
    return (False, d)

class Command(BaseCommand):
    args = ''
    help = 'Sets series and sourcefile dates to current timezone'

    def handle(self, *args, **options):
        fix = make_aware if settings.USE_TZ else make_naive
        count = 0
        for sf in SourceFile.objects.all():
            a,sf.start = fix(sf.start)
            b,sf.stop = fix(sf.stop)
            if a or b:
                count += 1
                sf.save()
        self.stdout.write('%d sourcefiles fixed' % count)
        for p in DataPoint.objects.all():
            a,p.date = fix(p.date)
            if a:
                p.save()
        self.stdout.write('%d datapoints fixed' % count)
                