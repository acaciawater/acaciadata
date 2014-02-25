from models import NeerslagStation, Station
from django.contrib.gis.geos import Point

def importneerslag(fil):
    with open(fil) as f:
        f.readline()
        line = f.readline()
        while line != '':
            words = line.split(',')
            if len(words)>7:
                x = float(words[6])
                y = float(words[7])
                NeerslagStation.objects.get_or_create(
                    naam = words[0],
                    nummer = int(words[1]),
                    location = Point(x,y)
                )
            line = f.readline()

def importstations(fil):
    with open(fil) as f:
        f.readline()
        line = f.readline()
        while line != '':
            words = line.split(',')
            if len(words)>8:
                x = float(words[7])
                y = float(words[8])
                Station.objects.get_or_create(
                    nummer = int(words[0]),
                    naam = words[1],
                    location = Point(x,y)
                )
            line = f.readline()

def importall():
    NeerslagStation.objects.all().delete()
    importneerslag('/home/theo/acacia/data/neerslag.csv')
    Station.objects.all().delete()
    importstations('/home/theo/acacia/data/nieuw.csv')
