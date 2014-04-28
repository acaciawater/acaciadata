'''
Created on Feb 26, 2014

@author: theo
'''
from knmi.models import NeerslagStation, Station
from .models import Datasource, Generator

import math
def distance(obj, pnt):
    dx = obj.location.x - pnt.x
    dy = obj.location.y - pnt.y
    return math.sqrt(dx*dx+dy*dy)

def closest_object(query,target):
    closest = None
    dist = 1e99
    for obj in query:
        d = distance(obj, target)
        if d < dist:
            closest = obj
            dist = d
    return closest

def meteo2locatie(loc,user):
    ''' Meteo datasources toevoegen aan meetlocatie '''
    
    p = loc.location

#     stns = Station.objects.distance(p).order_by('distance')
#     stn = stns[0]
    stn = closest_object(Station.objects.all(),p)
    name='Meteostation %s ' % stn.naam
    try:
        df = Datasource.objects.get(name = name, meetlocatie = loc)
    except:
        df = Datasource(name = name, meetlocatie = loc)
    df.generator = Generator.objects.get(name='KNMI Meteostation')
    generator = df.get_generator_instance()
    df.url = generator.url + '?stns=%d&start=20140101' % stn.nummer
    df.user=user
    df.save()
    df.download()
    df.update_parameters()
    
    #stns = NeerslagStation.objects.distance(p).order_by('distance')
    #stn = stns[0]
    stn = closest_object(NeerslagStation.objects.all(),p)
    name='Neerslagstation %s ' % stn.naam
    try:
        df = Datasource.objects.get(name = name, meetlocatie = loc)
    except:
        df = Datasource(name = name, meetlocatie = loc)
    df.generator = Generator.objects.get(name='KNMI Neerslagstation')
    generator = df.get_generator_instance()
    df.url = generator.url + '?stns=%d&start=20140101' % stn.nummer
    df.user=user
    df.save()
    df.download()
    df.update_parameters()

    name='Regenradar %s ' % loc.name
    try:
        df = Datasource.objects.get(name = name, meetlocatie = loc)
    except:
        df = Datasource(name = name, meetlocatie = loc)
    df.generator = Generator.objects.get(name='Regenradar')
    generator = df.get_generator_instance()
    df.url = generator.url
    df.config = '{"x": %g, "y": %g}' % (p.x, p.y)
    df.user=user
    df.save()
    df.download()
    df.update_parameters()
    
    