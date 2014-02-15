'''
Created on Feb 12, 2014

@author: theo
'''

import matplotlib.pyplot as plt
from matplotlib import rcParams
#rcParams['font.family'] = 'sans-serif'
#rcParams['font.sans-serif'] = ['Tahoma']
rcParams['font.size'] = '8'

def save_thumbnail(series,imagefile,kind='line'):
    plt.figure()
    options = {'figsize': (6,2), 'grid': False, 'xticks': [], 'legend': False}
    if kind == 'column':
        series.plot(kind='bar', **options)
    elif kind == 'area':
        x = series.index
        y = series.values
        series.plot(**options)
        plt.fill_between(x,y)
    else:
        series.plot(**options)
    plt.savefig(imagefile,transparent=True)
    plt.close()
    
def thumbtag(imagefile):
    url = "/media/%s" % imagefile
    return '<a href="%s"><img src="%s" height="50px"\></a>' % (url, url)
