'''
Created on Jun 3, 2014

@author: theo
'''
from .models import Well, Screen
import logging
import matplotlib.pyplot as plt
from matplotlib import rcParams
from StringIO import StringIO

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
    plt.title(screen)
    plt.ylabel('m tov NAP')
    img = StringIO() 
    plt.savefig(img,bbox_inches='tight', format='png')
    plt.close()    
    return img.getvalue()

def chart_for_well(well):
    plt.figure(figsize=(15,5))
    plt.grid(linestyle='-', color='0.9')
    count = 0
    y = []
    for screen in well.screen_set.all():
        data = screen.get_levels('nap')
        if len(data)>0:
            x,y = zip(*data)
            plt.plot_date(x, y, '-', label=screen)
            count += 1
            
    y = [screen.well.maaiveld] * len(x)
    plt.plot_date(x, y, '-', label='maaiveld')

    plt.title(well)
    plt.ylabel('m tov NAP')
    if count > 0:
        plt.legend()
    
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
