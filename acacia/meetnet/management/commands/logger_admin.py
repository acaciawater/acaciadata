from django.core.management.base import BaseCommand
from acacia.meetnet.models import Datalogger
from datetime import timedelta

class Command(BaseCommand):
    args = ''
    help = 'Administer loggers'

    def add_arguments(self,parser):
        parser.add_argument('cmd', help = 'admin command')
        parser.add_argument('device', help = 'device number')

    def handle(self, *args, **options):
        cmd = options.get('cmd')
        if cmd == 'move':
            pass
            