'''
Created on Feb 26, 2014

@author: theo
'''
from knmi.models import NeerslagStation, Station
from .models import Datasource, Generator

def meteo2locatie(loc,user):
    ''' Meteo datasources toevoegen aan meetlocatie '''
    
    p = loc.location

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
    
    stns = Station.objects.distance(p).order_by('distance')
    stn = stns[0]
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
    
    stns = NeerslagStation.objects.distance(p).order_by('distance')
    stn = stns[0]
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
    