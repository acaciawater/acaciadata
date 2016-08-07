'''
Created on May 18, 2014

@author: theo
'''
from django.core.management.base import BaseCommand
from acacia.mqtt.models import stop

class Command(BaseCommand):
    args = ''
    help = 'Stop mqtt server'

    def handle(self, *args, **options):
        stop()
        print 'Server stopped'
        