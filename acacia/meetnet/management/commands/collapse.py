from django.core.management.base import BaseCommand
from acacia.meetnet.models import Datalogger
from datetime import timedelta

class Command(BaseCommand):
    args = ''
    help = 'Collapse loggerpos instances'

    def handle(self, *args, **options):
        tolerance = timedelta(hours = 2)
        for logger in Datalogger.objects.all():
            posquery = logger.loggerpos_set.order_by('screen').order_by('start_date')
            poslist = list(posquery)
            p1 = None
            for p in poslist:
                print p, p.start_date.date(), p.end_date.date(), p.refpnt, p.depth,
                if p1 is None:
                    p1 = p
                else:
                    p2 = p
                    # if this installation starts more than 2h after previous, dont collapse installations
                    continuous = p1.end_date is None or p.start_date - p1.end_date <= tolerance
                    if continuous and p.screen == p1.screen and p.refpnt == p1.refpnt and p.depth == p1.depth:
                        # same screen, top, depth and continuous: collapse
                        if p1.end_date is None or p.end_date > p1.end_date:
                            p1.end_date = p.end_date
                            p1.save()
                        for f in p.files.all():
                            p1.files.add(f)
                        p.delete()
                        print 'Collapsed'
                        continue
                    else:
                        p1 = p2
                print 'Kept'
                continue
