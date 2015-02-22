'''
Created on Feb 13, 2014

@author: theo
'''
import datetime
from optparse import make_option
from django.core.management.base import BaseCommand
from ...models import Network, Well
#from ...dino import Dino
from acacia.data.generators.dino import Dino
from django.contrib.gis.geos import Point

def parsenum(text,num=float,default=0):
    try:
        return num(text)
    except ValueError:
        return default
    
class Command(BaseCommand):
    args = ''
    help = 'Importeer dino zipfile'
    option_list = BaseCommand.option_list + (
            make_option('--net',
                action='store',
                type = 'int',
                dest = 'netid',
                help='netwerk id',
                default = 1),
            make_option('--file',
                action='store',
                type = 'string',
                dest = 'dino',
                help = 'zipfile van dinoloket',
                default = None),
        )

    def handle(self, *args, **options):
        fname = options.get('dino')
        if fname:
            dino=Dino()
            netid = options.get('netid')
            network,created = Network.objects.get_or_create(pk=netid)
            network.well_set.filter(nitg = None).delete()
            for f,d in dino.iter_zip(fname): 
                try:
                    name = d['Locatie']
                    nr = parsenum(d['Filternummer'],int,1)
                    try:
                        datum = datetime.datetime.strptime(d['Datum maaiveld gemeten'],'%d-%m-%Y')
                    except:
                        datum = datetime.date.today()
                    x = float(d['X-coordinaat'])
                    y = float(d['Y-coordinaat'])
                    loc = Point(x,y)
                    maaiveld = parsenum(d['Maaiveld (cm t.o.v. NAP)']) / 100
                    refpnt = parsenum(d['Meetpunt (cm t.o.v. NAP)']) / 100
                    # replace existing well
                    #network.well_set.filter(nitg=name).delete()
                    well, created = network.well_set.get_or_create(nitg=name, defaults={'name': name, 'maaiveld': maaiveld, 'refpnt': refpnt, 'location': loc, 'date':datum})
                    top = parsenum(d['Bovenkant filter (cm t.o.v. NAP)']) / 100
                    bottom = parsenum(d['Onderkant filter (cm t.o.v. NAP)']) / 100
                    filter,newfilter = well.screen_set.get_or_create(nr=nr, defaults = {'top': top, 'bottom': bottom})
                    print filter
#                     for s in d['standen']:
#                         try:
#                             date = s[2]
#                             value = s[5]
#                             if len(date)>0 and len(value)>0:
#                                 peildatum = datetime.datetime.strptime(date+' 12:00:00','%d-%m-%Y %H:%M:%S')
#                                 standnap = float(value) / 100
#                                 if newfilter:
#                                     filter.datapoint_set.create(date=peildatum,level=standnap)
#                                 else:
#                                     filter.datapoint_set.get_or_create(date=peildatum,defaults={'level': standnap})
#                         except Exception as e:
#                             print name, nr, e
                except Exception as e:
                    print name, nr, e