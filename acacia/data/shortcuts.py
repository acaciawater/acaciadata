'''
Created on Feb 26, 2014

@author: theo
'''
from knmi.models import NeerslagStation, Station
from .models import Datasource, Generator

def meteo2locatie(loc,user):
    ''' Meteo datasources toevoegen aan meetlocatie '''
    
    p = loc.location
    
    stns = Station.closest(p, 3)
    for stn in stns:
        name='Meteostation %s ' % stn.naam
        try:
            df = Datasource.objects.get(name = name, meetlocatie = loc)
        except:
            df = Datasource(name = name, meetlocatie = loc)
        df.generator = Generator.objects.get(name='KNMI Meteostation')
        generator = df.get_generator_instance()
        df.url = generator.url + '?stns=%d&start=20150101' % stn.nummer
        df.user=user
        df.save()
        df.download()
        df.update_parameters()
    
    stns = NeerslagStation.closest(p, 3)
    for stn in stns:
        name='Neerslagstation %s ' % stn.naam
        try:
            df = Datasource.objects.get(name = name, meetlocatie = loc)
        except:
            df = Datasource(name = name, meetlocatie = loc)
        df.generator = Generator.objects.get(name='KNMI Neerslagstation')
        generator = df.get_generator_instance()
        df.url = generator.url + '?stns=%d&start=20150101' % stn.nummer
        df.user=user
        df.save()
        df.download()
        df.update_parameters()
