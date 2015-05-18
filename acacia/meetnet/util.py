'''
Created on Jun 3, 2014

@author: theo
'''
from .models import Well, Screen
import logging, datetime
import matplotlib.pyplot as plt
from matplotlib import rcParams
from StringIO import StringIO
from acacia.data.models import DataPoint
import math, pytz

rcParams['font.family'] = 'sans-serif'
rcParams['font.size'] = '8'

logger = logging.getLogger(__name__)

def chart_for_screen(screen):
    plt.figure(figsize=(15,5))
    plt.grid(linestyle='-', color='0.9')
    data = screen.get_levels('nap')
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
    fig=plt.figure(figsize=(15,5))
    ax=fig.gca()
    datemin=datetime.datetime(2014,1,1)
    datemax=datetime.datetime(2015,1,1)
    ax.set_xlim(datemin, datemax)
    plt.grid(linestyle='-', color='0.9')
    count = 0
    y = []
    for screen in well.screen_set.all():
        data = screen.get_levels('nap')
        if len(data)>0:
            x,y = zip(*data)
            plt.plot_date(x, y, '-', label=screen)
            count += 1

        hand = screen.get_hand('nap')
        if len(hand)>0:
            x,y = zip(*hand)
            plt.plot_date(x, y, 'ro', label='handpeiling')
            
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
        if logpos.refpnt is None or logpos.depth is None or logpos.baro is None:
            continue
        if seriesdata is  None:
            meteo = logpos.baro.meetlocatie().name
            series.description = 'Gecompenseerd voor luchtdruk van %s' % meteo
            print '  Luchtdruk:', meteo
        if logpos.baro in baros:
            baro = baros[logpos.baro]
        else:
            baro = logpos.baro.to_pandas() / 9.80638 # 0.1 hPa naar cm H2O
            baro = baro.tz_convert(tz)
            baros[logpos.baro] = baro
        for mon in logpos.monfile_set.all().order_by('start_date'):
            print ' ', logpos.logger, mon
            data = mon.get_data()['PRESSURE']
            data = series.do_postprocess(data).tz_localize(tz)
            data = data - baro
            data.dropna(inplace=True)
            data = data / 100 + (logpos.refpnt - logpos.depth)
            if seriesdata is None:
                seriesdata = data
            else:
                seriesdata = seriesdata.append(data)
                
    series.datapoints.all().delete()
    if seriesdata is not None:
        seriesdata = seriesdata.groupby(level=0).last()
        seriesdata.sort(inplace=True)
        datapoints=[]
        for date,value in seriesdata.iteritems():
            value = float(value)
            if math.isnan(value) or date is None:
                continue
            datapoints.append(DataPoint(series=series, date=date, value=value))
        series.datapoints.bulk_create(datapoints)
        series.unit = 'm tov NAP'
        series.make_thumbnail()
        series.save()
    