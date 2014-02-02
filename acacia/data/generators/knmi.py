'''
Created on Jan 24, 2014

@author: theo
'''
import pandas as pd
import logging
import json
import urllib2

logger = logging.getLogger(__name__)

from generator import Generator

class Meteo(Generator):
    ''' Dag waarden van meteostation(s) ophalen '''
    
    #url = 'http://www.knmi.nl/klimatologie/daggegevens/getdata_uur.cgi'
    #url = 'http://www.knmi.nl/klimatologie/daggegevens/getdata_dag.cgi'
        
    def get_header(self, f):
        header = {}
        line = f.readline()
        while line != '':
            if line.startswith('# STN,YYYYMMDD'):
                columns = [w.strip() for w in line[2:].split(',')]
                header['COLUMNS'] = [c for c in columns if len(c)>0]
                f.readline()
                break
            else:
                line = f.readline()
        return header
    
    def get_data(self, f, **kwargs):
        header = self.get_header(f)
        columns = header['COLUMNS']
        data = pd.read_csv(f, header=0, names=columns, comment = '#', index_col = [0,1], parse_dates = True)
        return [header,data]

    def get_parameters(self, fil):
        header = self.get_header(fil)
        names = header['COLUMNS'][2:] # eerste 2 zijn station en datum
        params = [{'name': name, 'description' : name, 'unit': 'unknown'} for name in names]  
        return params
    
class Neerslag(Meteo):
    '''Dagwaarden van neerslagstations ophalen'''
    #url = 'http://www.knmi.nl/klimatologie/monv/reeksen/getdata_rr.cgi'
    
    def get_header(self, f):
        header = {}
        line = f.readline()
        while line != '':
            if line.startswith('STN,YYYYMMDD'):
                columns = [w.strip() for w in line.split(',')]
                header['COLUMNS'] = [c for c in columns if len(c)>0]
                break
            else:
                line = f.readline()
        return header

    def get_data(self, f, **kwargs):
        header = self.get_header(f)
        names = header['COLUMNS']
        names.append('NAME')
        data = pd.read_csv(f, header=None, names=names, comment = '#', index_col = [0,1], parse_dates = True)
        return [header,data]
