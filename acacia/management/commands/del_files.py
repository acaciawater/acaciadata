from django.core.management.base import BaseCommand
from acacia.meetnet.models import Well
from dateutil import parser
from django.utils.timezone import get_current_timezone

class Command(BaseCommand):
    args = ''
    help = 'Delete selected sourcefiles'
    
    def add_arguments(self, parser):
        parser.add_argument('-n','--no-delete',
                action='store_true',
                dest='dry',
                default=False,
                help="Dry run: don't delete the files")
        parser.add_argument('-f','--force',
                action='store_true',
                dest='force',
                default=False,
                help="Force deletion of files")
        parser.add_argument('-w','--well',
                dest='well',
                default=None,
                help="Well name")
        parser.add_argument('-s','--screen',
                dest='screen',
                default='1',
                help="screen number (default=1)")
        parser.add_argument('-b','--begin',
                dest='begin',
                default=None,
                help="select files that start after this date")
        parser.add_argument('-e','--end',
                dest='end',
                default=None,
                help="select files that end before this date")

    def handle(self, *args, **options):
        dry = options.get('dry')
        well_name = options.get('well')
        screen_nr = options.get('screen')
        begin = options.get('begin')         
        end = options.get('end')
        tz = get_current_timezone()
        if begin:
            begin = tz.localize(parser.parse(begin))
        if end:
            end = tz.localize(parser.parse(end))
        
        force = options.get('force')
        if end is None or begin is None and not force:
            print('Must use --force to delete files without specifying begin or end date')
            return
        
        well = Well.objects.get(name__iexact=well_name)
        screen = well.screen_set.get(nr = int(screen_nr))
        for ds in screen.mloc.datasource_set.all():
            query = ds.sourcefiles.all()
            if begin:
                query = query.filter(start__gt=begin)
            if end:
                query = query.filter(stop__lt=end)
            print('Deleting {} files for {}'.format(query.count(), screen))
            if not dry:
                query.delete()