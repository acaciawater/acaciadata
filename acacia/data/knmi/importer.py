from models import NeerslagStation, Station
from django.contrib.gis.geos import Point

def importneerslag(fil):
    with open(fil) as f:
        f.readline()
        line = f.readline()
        while line != '':
            words = line.split(',')
            if len(words)>9:
                lon = float(words[8])
                lat = float(words[9])
                NeerslagStation.objects.get_or_create(
                    naam = words[0],
                    nummer = int(words[1]),
                    xcoord=float(words[6]),
                    ycoord=float(words[7]),
                    lon = lon,
                    lat = lat,
                    location = Point(lon,lat)
                )
            line = f.readline()

def importstations(fil):
    with open(fil) as f:
        f.readline()
        line = f.readline()
        while line != '':
            words = line.split(',')
            if len(words)>8:
                lon = float(words[5])
                lat = float(words[6])
                Station.objects.get_or_create(
                    nummer = int(words[0]),
                    naam = words[1],
                    xcoord = float(words[7]),
                    ycoord = float(words[8]),
                    lon = lon,
                    lat = lat,
                    location = Point(lon,lat)
                )
            line = f.readline()

def importall():
    NeerslagStation.objects.all().delete()
    importneerslag('/home/theo/acacia/data/neerslag.csv')
    Station.objects.all().delete()
    importstations('/home/theo/acacia/data/nieuw.csv')
