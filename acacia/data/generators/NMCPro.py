import pandas as pd
import logging
import json
import urllib2
logger = logging.getLogger(__name__)

from generator import Generator
class NMCPro(Generator):
        
    def __init__(self, *args, **kwargs):
        super(NMCPro, self).__init__(args,kwargs)
        self.args = {'url': 'ftp://theo:Heinis14@grondwatertoolbox.nl/home/arjen/Breezand/Processed'}

    def get_default_args(self):
        return json.dumps(self.args)
    
    def get_header(self, f):
        sections = {}
        f.readline()
        colnames = [n.strip() for n in f.readline().split(',')]
        sections['COLUMNS'] = colnames[2:] # first two are date and time
        return sections
    
    def get_file(self, path):
        response = urllib2.urlopen(self.url + '/' + path)
        return response
        
    def get_data(self, f, **kwargs):
        header = self.get_header(f)
        line = f.readline()
        while line != '':
            if line.startswith('# STN,YYYYMMDD'):
                names = [w.strip() for w in line[2:].split(',')]
                data = pd.read_csv(f, header=0, names=names, comment = '#', index_col = [0,1], parse_dates = True)
                return [header,data]
            line = f.readline()
        return None

    def get_parameters(self, fil):
        header = self.get_header(fil)
        names = header['COLUMNS']
        params = [{'name': name, 'description' : name, 'unit': 'unknown'} for name in names]  
        return params
        
if __name__ == '__main__':
    nmc = NMCPro()
    data=nmc.get_data()
    print data
