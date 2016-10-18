# -*- coding: utf-8 -*-
'''
Created on Feb 13, 2014

@author: theo
'''
from django.core.management.base import BaseCommand
from optparse import make_option
from acacia.data.models import Datasource, Generator
import logging
try:
    import xml.etree.cElementTree as ET
except:
    import xml.etree.ElementTree as ET

class Command(BaseCommand):
    args = ''
    help = 'Check for port changes in decagon datasource'
    
    def add_arguments(self, parser):
        parser.add_argument('--pk',
                action='store',
                type = int,
                dest = 'pk',
                default = None,
                help = 'check single datasource')

    def handle(self, *args, **options):
        #logger = logging.getLogger('acacia.data')
        pk = options.get('pk', None)
        if pk is None:
            generator = Generator.objects.get(name = 'Decagon')
            datasources = generator.datasource_set.all()
        else:
            datasources = Datasource.objects.filter(pk=pk)
    
        for d in datasources:
            last = ''
            print d.name
            for f in d.sourcefiles.all().order_by('name'):
                tree = ET.ElementTree()
                try:
                    with open(f.file.path) as dxd:
                        tree.parse(dxd)
                except Exception as e:
                    print f.name, e
                    continue
                device = tree.find('Device')
                ports = device.findall('Configuration/Measurement/Ports/Port')
                #nports = len(ports)
                defs = [255]*5
                for elem in ports:
                    port = elem.attrib
                    value = port['value']
                    #sensor = port['sensor']
                    number = int(port['number'])-1
                    defs[number] = value
                line = ','.join(defs)
                if line != last:
                    print ','.join([f.name,line])
                    last = line
                