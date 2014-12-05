import logging
import urllib2
logger = logging.getLogger(__name__)

from generator import Generator
class NMCPro(Generator):
            
    def get_header(self, f):
        sections = {}
        self.skiprows = 0
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
        data = self.read_csv(f, header=0, skiprows = self.skiprows, names=names, comment = '#', index_col=[0], 
                           parse_dates = [0], na_values = ['----', '-------'])
        data.dropna(how='all',inplace=True)
        data.sort(inplace=True)
        print data.tail(10)
        return data

    def get_parameters(self, fil):
        header = self.get_header(fil)
        names = header['COLUMNS'][2:]
        params = {}
        for name in names:
            params[name] = {'description' : name, 'unit': '-'} 
        return params

class NMCJr(NMCPro):
    pass
        
if __name__ == '__main__':
    nmc = NMCPro()
    data=nmc.get_data()
    print data
