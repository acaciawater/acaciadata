from models import NeerslagStation, Station
from django.contrib.gis.geos import Point

def importneerslag(fil):
    with open(fil) as f:
        f.readline()
        line = f.readline()
        while line != '':
            words = line.split(',')
            if len(words)>7:
                x = float(words[7])
                y = float(words[8])
                NeerslagStation.objects.get_or_create(
                    naam = words[0],
                    nummer = int(words[1]),
                    zipfilename = words[2],
                    location = Point(x,y)
                )
            line = f.readline()

def importstations(fil):
    with open(fil) as f:
        f.readline()
        line = f.readline()
        while line != '':
            words = line.split(',')
            if len(words)>9:
                x = float(words[8])
                y = float(words[9])
                Station.objects.get_or_create(
                    nummer = int(words[0]),
                    naam = words[1],
                    zipfilename = words[2],
                    location = Point(x,y)
                )
            line = f.readline()

def importall():
    NeerslagStation.objects.all().delete()
    importneerslag('/media/sf_F_DRIVE/projdirs/knmi/neerslag.csv')
    Station.objects.all().delete()
    importstations('/media/sf_F_DRIVE/projdirs/knmi/nieuw.csv')
