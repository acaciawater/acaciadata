'''
Created on Jun 3, 2014

@author: theo
'''
from .models import Well, Screen
import logging
import matplotlib
matplotlib.use('agg')
import matplotlib.pylab as plt
from matplotlib import rcParams
from StringIO import StringIO
from acacia.data.models import DataPoint
import math, pytz
import numpy as np

rcParams['font.family'] = 'sans-serif'
rcParams['font.size'] = '8'

logger = logging.getLogger(__name__)

# thumbnail size and resolution
THUMB_DPI=72
THUMB_SIZE=(9,3) # inch

def chart_for_screen(screen):
    plt.figure(figsize=THUMB_SIZE)
    plt.grid(linestyle='-', color='0.9')
    data = screen.get_levels('nap')
    n = len(data) / (THUMB_SIZE[0]*THUMB_DPI)
    if n > 1:
        #use data thinning: take very nth row
        data = data[::n]
    if len(data)>0:
        x,y = zip(*data)
        plt.plot_date(x, y, '-')
        y = [screen.well.maaiveld] * len(x)
        plt.plot_date(x, y, '-')

    hand = screen.get_hand('nap')
    if len(hand)>0:
        x,y = zip(*hand)
        plt.plot_date(x, y, 'ro',label='handpeiling')

    plt.title(screen)
    plt.ylabel('m tov NAP')
    img = StringIO() 
    plt.savefig(img,bbox_inches='tight', format='png')
    plt.close()    
    return img.getvalue()

def chart_for_well(well):
    fig=plt.figure(figsize=THUMB_SIZE)
    ax=fig.gca()
    plt.grid(linestyle='-', color='0.9')
    count = 0
    y = []
    x = []
    for screen in well.screen_set.all():
        data = screen.get_levels('nap')
        n = len(data) / (THUMB_SIZE[0]*THUMB_DPI)
        if n > 1:
            #use data thinning: take very nth row
            data = data[::n]
        if len(data)>0:
            x,y = zip(*data)
            plt.plot_date(x, y, '-', label=screen)
            count += 1

        hand = screen.get_hand('nap')
        if len(hand)>0:
            x,y = zip(*hand)
            plt.plot_date(x, y, 'ro', label='handpeiling')
            
    if len(x):
        y = [screen.well.maaiveld] * len(x)
        plt.plot_date(x, y, '-', label='maaiveld')

    plt.title(well)
    plt.ylabel('m tov NAP')
    if count > 0:
        leg=plt.legend()
        leg.get_frame().set_alpha(0.3)
    
    img = StringIO() 
    plt.savefig(img,format='png',bbox_inches='tight')
    plt.close()    
    return img.getvalue()

def encode_chart(chart):
    return 'data:image/png;base64,' + chart.encode('base64')

def make_chart(obj):
    if isinstance(obj,Well):
        return chart_for_well(obj)
    elif isinstance(obj,Screen):
        return chart_for_screen(obj)
    else:
        raise Exception('make_chart(): object must be a well or a screen')
    
def make_encoded_chart(obj):
    return encode_chart(make_chart(obj))

def recomp(screen,series,baros={},tz=pytz.FixedOffset(60)):
    ''' re-compensate timeseries for screen '''

    seriesdata = None
    for logpos in screen.loggerpos_set.all().order_by('start_date'):
        if logpos.refpnt is None:
            logger.warning('Referentiepunt ontbreekt voor {pos}'.format(pos=logpos))
            continue
        if logpos.depth is None:
            logger.warning('Inhangdiepte ontbreekt voor {pos}'.format(pos=logpos))
            continue
        if logpos.baro is None:
            logger.warning('Barometer ontbreekt voor {pos}'.format(pos=logpos))
            continue
        if seriesdata is None:
            meteo = logpos.baro
            logger.info('Compenseren voor luchtdrukreeks {}'.format(meteo))
        if logpos.baro in baros:
            baro = baros[logpos.baro]
        else:
            baro = logpos.baro.to_pandas()

            # if baro datasource = KNMI then convert from hPa to cm H2O
            dsbaro = logpos.baro.getDatasource()
            if dsbaro:
                gen = dsbaro.generator
                if 'knmi' in gen.name.lower() or 'knmi' in gen.classname.lower():
                    # TODO: use g at  baro location, not well location
                    baro = baro / (screen.well.g or 9.80638)
            
            baro = baro.tz_convert(tz)
            baros[logpos.baro] = baro
        for mon in logpos.monfile_set.all().order_by('start_date'):
            print ' ', logpos.logger, mon
            data = mon.get_data()['PRESSURE']
            data = series.do_postprocess(data).tz_localize(tz)
            
            adata, abaro = data.align(baro)
            abaro = abaro.interpolate(method='time')
            abaro = abaro.reindex(data.index)
            data = data - abaro
            data.dropna(inplace=True)

            #clear datapoints with less than 10 cm of water
            data[data<10] = np.nan
            
            data = data / 100 + (logpos.refpnt - logpos.depth)
            if seriesdata is None:
                seriesdata = data
            else:
                seriesdata = seriesdata.append(data)
                
    if seriesdata is not None:
        seriesdata = seriesdata.groupby(level=0).last()
        seriesdata.sort(inplace=True)
        datapoints=[]
        for date,value in seriesdata.iteritems():
            value = float(value)
            if math.isnan(value) or date is None:
                continue
            datapoints.append(DataPoint(series=series, date=date, value=value))
        series.datapoints.all().delete()
        series.datapoints.bulk_create(datapoints)
        series.unit = 'm tov NAP'
        series.make_thumbnail()
        series.save()
    
from acacia.data.knmi.models import NeerslagStation, Station
from acacia.data.models import ProjectLocatie, Generator

def createmeteo(request, well):
    ''' Create datasources with meteo data for a well '''

    def docreate(name,closest,gen,start):
        instance = gen.get_class()()
        ploc, created = project.projectlocatie_set.get_or_create(name = name, defaults = {'description': name, 'location': closest.location})
        mloc, created = ploc.meetlocatie_set.get_or_create(name = name, defaults = {'description': name, 'location': closest.location})
        if created:
            logger.info('Meetlocatie {} aangemaakt'.format(name))   
        ds, created = mloc.datasources.get_or_create(name = name, defaults = {'description': name,'generator': gen, 'user': user, 'timezone': 'UTC',
                                                     'url': instance.url + '?stns={stn}&start={start}'.format(stn=closest.nummer,start=start)})
        if created:
            ds.download()
            ds.update_parameters()
            
            for p in ds.parameter_set.filter(name__in=candidates):
                try:
                    series, created = p.series_set.get_or_create(name = p.name, description = p.description, unit = p.unit, user = request.user)
                    series.replace()
                except Exception as e:
                    logger.error('ERROR creating series %s: %s' % (p.name, e))
    
    user = request.user

    candidates = ['PG', 'EV24', 'RD', 'RH', 'P', 'T']
    
    ploc = ProjectLocatie.objects.get(name=well.name)
    project = ploc.project
    
    gen = Generator.objects.get(classname__icontains='KNMI.meteo')
    closest = Station.closest(well.location)
    name = 'Meteostation {} (dagwaarden)'.format(closest.naam)
    docreate(name,closest,gen,'20140501')

    gen = Generator.objects.get(classname__icontains='KNMI.neerslag')
    closest = NeerslagStation.closest(well.location)
    name = 'Neerslagstation {}'.format(closest.naam)
    docreate(name,closest,gen,'20140501')

    gen = Generator.objects.get(classname__icontains='KNMI.uur')
    closest = Station.closest(well.location)
    name = 'Meteostation {} (uurwaarden)'.format(closest.naam)
    docreate(name,closest,gen,'2014050101')
