'''
Created on Apr 25, 2017

@author: theo
'''
import datetime
from optparse import make_option
from django.core.management.base import BaseCommand
from ...models import Network, Well
import csv
from django.core.exceptions import ObjectDoesNotExist

class Command(BaseCommand):
    args = ''
    help = 'Importeer csv file met NITG nummers'
    option_list = BaseCommand.option_list + (
            make_option('--file',
                action='store',
                type = 'string',
                dest = 'fname',
                help = 'bestandsnaam',
                default = None),
        )

    def handle(self, *args, **options):
        fname = options.get('fname')
        if fname:
            with open(fname) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    put = row['Alternatieve aanduiding']
                    try:
                        well = Well.objects.get(name=put)
                        well.nitg = row['Nitg-nummer']
                        well.maaiveld = float(row['Maaiveldhoogte (m)'])
                        well.save()
                        print put,'Ok'
                    except Well.DoesNotExist:
                       print put,'Skipped'