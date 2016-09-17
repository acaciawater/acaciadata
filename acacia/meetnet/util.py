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
        if seriesdata is  None:
            meteo = logpos.baro.meetlocatie().name
            logger.info('Compenseren voor luchtdruk van {}'.format(meteo))
        if logpos.baro in baros:
            baro = baros[logpos.baro]
        else:
            #baro = logpos.baro.to_pandas() / 9.80638 # 0.1 hPa naar cm H2O
            baro = logpos.baro.to_pandas() #in cm H2O !!
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
    