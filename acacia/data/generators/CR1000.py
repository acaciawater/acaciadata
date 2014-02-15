'''
Created on Jan 28, 2014

@author: theo
'''
import csv
import pandas as pd

import logging
logger = logging.getLogger(__name__)

from generator import Generator
class CR1000(Generator):

    def get_header(self, f):
        sections = {}
        header = f.readlines(4)
        reader = csv.reader(header)
        row = reader.next()
        sections['HEADER'] = row
        row = reader.next()
        sections['COLUMNS'] = row
        row = reader.next()
        sections['UNITS'] = row
        row = reader.next()
        sections['AGGR'] = row
        return sections
    
    def get_data(self, f, **kwargs):
        header = self.get_header(f)
        names = header['COLUMNS']
        data = pd.read_csv(f, header=None, names=names, parse_dates = True )
        return [header, data]

    def upload(self,f,**kwargs):
        pass

    def get_parameters(self, fil):
        header = self.get_header(fil)
        names = header['COLUMNS']
        units = header['UNITS']
        params = [{'name': name, 'description' : name, 'unit': unit} for name,unit in zip(names,units)]  
        return params
        
if __name__ == '__main__':
    cr = CR1000()
    with open('/home/theo/acacia/data/RuweData_Loggers_v_6aug_2013/CR1000_regulated_levelcontroltable.dat') as f:
        data=cr.get_data(f)
    print data[0]
    flow = data[1]['BattV_Avg']
    print flow
