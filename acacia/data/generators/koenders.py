import numpy as np
import logging
import urllib2
import datetime
from pytz import timezone
logger = logging.getLogger(__name__)

from generator import Generator

def convtime(txt,tz=None):
    try:
        dt = datetime.datetime.strptime(txt,'%Y-%m-%d %H:%M:%S')
        if tz is not None:
            dt = tz.localize(dt)
        return dt
    except:
        return None

def date_parser(dt):
    ''' date parser for pandas read_csv '''
    # Koenders' time is synced with internet time server, so always up-to-date
    tz = timezone('Europe/Amsterdam')
    return np.array([convtime(t,tz) for t in dt])

class Koenders(Generator):
            
    def get_header(self, f):
        return {'COLUMNS': ['Date', 'Puls1', 'Puls2', 'Batt'],}
    
    def get_file(self, path):
        return urllib2.urlopen(self.url + '/' + path)
        
    def get_data(self, f, **kwargs):
        header = self.get_header(f)
        names = header['COLUMNS']
        data = self.read_csv(f, header=0, names=names, index_col=[0], usecols = [0,2,3,7],  parse_dates = True)
        data.dropna(inplace=True)
        return data

    def get_parameters(self, fil):
        header = self.get_header(fil)
        names = header['COLUMNS'][1:]
        params = {}
        for name in names:
            params[name] = {'description' : name, 'unit': '-'} 
        return params

if __name__ == '__main__':
    k = Koenders()
    with open('/home/theo/data/koenders/S5070.LOG') as f:
        data = k.get_data(f)
        print data.index.min(), data.index.max()
    