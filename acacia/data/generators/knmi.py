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
        descr = {}
        header['DESCRIPTION'] = descr
        line = f.readline()
        while line != '':
            if line.startswith('# YYYYMMDD'):
                line = f.readline()
                while line.startswith('#'):
                    if line.startswith('# STN,YYYYMMDD'):
                        columns = [w.strip() for w in line[2:].split(',')]
                        header['COLUMNS'] = [c for c in columns if len(c)>0]
                        #f.readline()
                        break
                    else:
                        eq = line.find('=')
                        if eq>0:
                            key = line[1:eq].strip()
                            val = line[eq+1:].strip()
                            descr[key]=val
                        line = f.readline()
                break
            else:
                line = f.readline()
        return header
    
    def get_data(self, f, **kwargs):
        header = self.get_header(f)
        columns = header['COLUMNS']
        data = pd.read_csv(f, header=0, names=columns, comment = '#', index_col = 1, parse_dates = True)
        return data

    def get_parameters(self, fil):
        header = self.get_header(fil)
        names = header['COLUMNS'][2:] # eerste 2 zijn station en datum
        desc = header['DESCRIPTION']
        params = [{'name': name, 'description' : desc.get(name,name), 'unit': 'unknown'} for name in names]  
        return params
    
class Neerslag(Meteo):
    '''Dagwaarden van neerslagstations ophalen'''
    #url = 'http://www.knmi.nl/klimatologie/monv/reeksen/getdata_rr.cgi'
    
    def get_header(self, f):
        header = {}
        descr = {}
        header['DESCRIPTION'] = descr
        for i in range(0,9):
            line = f.readline()
        lastkey = ''
        while line != '':
            if line.strip() == '':
                line = f.readline()
                break
            key = line[:9].strip()
            if len(key) > 0:
                descr[key] = line[11:].strip()
                lastkey = key
            else:
                key = lastkey
                descr[key] = descr[key] + line[11:].strip()
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
        data = pd.read_csv(f, header=None, names=names, comment = '#', index_col = 1, parse_dates = True)
        return data
