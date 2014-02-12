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
        sections['COLUMNS'] = colnames
        return sections
    
    def get_file(self, path):
        response = urllib2.urlopen(self.url + '/' + path)
        return response
        
    def get_data(self, f, **kwargs):
        header = self.get_header(f)
        names = header['COLUMNS']
        data = pd.read_csv(f, header=0, names=names, comment = '#', index_col = [0], 
                           parse_dates = True, dayfirst=True, na_values = ['----', '-------'])
        return data

    def get_parameters(self, fil):
        header = self.get_header(fil)
        names = header['COLUMNS']
        params = [{'name': name, 'description' : name, 'unit': 'unknown'} for name in names]  
        return params
        
if __name__ == '__main__':
    nmc = NMCPro()
    data=nmc.get_data()
    print data
