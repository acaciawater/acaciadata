'''
Created on May 18, 2014

@author: theo
'''
from django.core.management.base import BaseCommand
from acacia.mqtt.models import start

class Command(BaseCommand):
    args = ''
    help = 'Start mqtt server'

    def handle(self, *args, **options):
        start()
        print 'Server started'
        