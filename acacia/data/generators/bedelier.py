import pandas as pd
import logging
import urllib2
logger = logging.getLogger(__name__)

from generator import Generator

class OWB(Generator):
        
    def get_header(self, f):
        cols = f.readline().split(';')
        sections = {}
        sections['COLUMNS'] = cols
        return sections
            
    def get_data(self, f, **kwargs):
        header = self.get_header(f)
        data = pd.read_csv(f, header=None, sep = ';', index_col = 0, parse_dates = {'datum': [0,1]}, dayfirst = True)
        if data is not None:
            names = header['COLUMNS'][2:]
            #names.append('Laatste kolom')
            data.columns = names
        return data

    def get_parameters(self, fil):
        header = self.get_header(fil)
        names = header['COLUMNS'][2:]
        params = {}
        for name in names:
            params[name] = {'description' : name, 'unit': '-'} 
        return params
    
if __name__ == '__main__':
    with open('/home/theo/acacia/data/Breezand/LogFile140221.csv') as f:
        o = OWB()
        data = o.get_data(f)
        print data
