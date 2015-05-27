import numpy as np
import logging
import datetime
import pytz
from .campbell import CR1000

logger = logging.getLogger(__name__)

from generator import Generator

def convtime(txt,tz=None):
    try:
        dt = datetime.datetime.strptime(txt,'%Y-%m-%d %H:%M:%S')
        if tz is not None:
            dt = dt.replace(tzinfo=tz)
        return dt
    except:
        return None

def date_parser(dt):
    ''' date parser for pandas read_csv '''
    # Koenders' time is fixed at CET (UTC+1)
    tz = pytz.timezone('CET')
    return np.array([convtime(t,tz) for t in dt])

class Koenders(Generator):
            
    def get_header(self, f):
        return {'COLUMNS': ['Date', 'Puls1', 'Puls2', 'Batt'],}
            
    def get_data(self, f, **kwargs):
        header = self.get_header(f)
        names = header['COLUMNS']
        data = self.read_csv(f, header=None, names=names, index_col=[0], usecols = [0,2,3,7],  
                             parse_dates = True, date_parser = date_parser)
        data.dropna(inplace=True)
        return data

    def get_parameters(self, fil):
        header = self.get_header(fil)
        names = header['COLUMNS'][1:]
        params = {}
        for name in names:
            params[name] = {'description' : name, 'unit': '-'} 
        return params

class Koenders52(Koenders):
    def get_header(self, f):
        return {'COLUMNS': ['Datumtijd','pulswaarde','mmwater','ecwaarde','kanaal4','diwaarde','batterij','status']}
    
    def get_data(self, f, **kwargs):
        header = self.get_header(f)
        names = header['COLUMNS']
        data = self.read_csv(f, header=0, names=names, index_col=[0], usecols=[0,2,3,4,5,6,7,8], parse_dates = True, date_parser=date_parser)
        data.dropna(inplace=True)
        return data

class Koenders5247(CR1000):
    pass

# class Koenders5247(Koenders52):
#     def get_header(self, f):
#         sections = {}
#         line1 = f.readline()
#         line2 = f.readline()
#         line3 = f.readline()
#         line4 = f.readline()
#         colnames = [n.strip('"\r\n') for n in line2.split(',')]
#         sections['COLUMNS'] = colnames
#         return sections
#     
#     def get_data(self, f, **kwargs):
#         header = self.get_header(f)
#         names = header['COLUMNS']
#         data = self.read_csv(f, header=None, names=names, index_col=[0], parse_dates = True)
#         data.dropna(inplace=True)
#         return data

if __name__ == '__main__':
    k = Koenders5247()
    with open('/home/theo/data/koenders/S5247 Acacia water CR1000_meetwaarde.dat') as f:
        data = k.get_data(f)
        print data.index.min(), data.index.max()

        