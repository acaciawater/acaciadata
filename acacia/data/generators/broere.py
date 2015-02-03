import logging
import numpy as np
import datetime

logger = logging.getLogger(__name__)

from generator import Generator

def date_parser(dt):
    ''' date parser for pandas read_csv '''
    return np.array([datetime.datetime.strptime(t,'%Y-%m-%d %H:%M:%S') for t in dt if t is not None])

class NMCPro(Generator):
            
    def __init__(self, *args, **kwargs):        
        super(NMCPro,self).__init__(*args, **kwargs)
        self.dayfirst = kwargs.get('dayfirst', False)

    def get_header(self, f):
        sections = {}
        self.skiprows = 1
        line = f.readline()
        while not (line.startswith('Date') or line.startswith('Datum')):
            line = f.readline()
            self.skiprows += 1
            if not line:
                return {}
        colnames = [n.strip() for n in line.split(',')]
        sections['COLUMNS'] = colnames
        return sections
    
    def get_data(self, f, **kwargs):
        header = self.get_header(f)
        names = header['COLUMNS']
        data = self.read_csv(f, header=None, skiprows = self.skiprows, names=names, comment = '#', index_col=0, 
                           parse_dates=0, dayfirst = self.dayfirst, na_values = ['----', '-------'])
        data.dropna(how='all',inplace=True)
        data.sort(inplace=True)
        return data

    def get_parameters(self, fil):
        header = self.get_header(fil)
        names = header['COLUMNS'][2:]
        params = {}
        for name in names:
            params[name] = {'description' : name, 'unit': '-'} 
        return params

class NMCJr(NMCPro):

    def __init__(self, *args, **kwargs):        
        super(NMCJr,self).__init__(*args, **kwargs)
        
if __name__ == '__main__':
    nmc = NMCPro()
    data=nmc.get_data()
    print data
