'''
Created on Jan 28, 2014

@author: theo
'''
import csv
import logging
logger = logging.getLogger(__name__)

from generator import Generator
class CR1000(Generator):

    def get_header(self, f):
        
        def rd(f):
            return [n.strip('"\r\n') for n in f.readline().split(',')]

        f.seek(0)
        sections = {}
        sections['HEADER'] = rd(f) 
        sections['COLUMNS'] = rd(f)
        sections['UNITS'] = rd(f)
        sections['AGGR'] = rd(f)
        if self.engine == 'python':
            self.skiprows = 4
        return sections

    def get_data(self, f, **kwargs):
        header = self.get_header(f)
        names = header['COLUMNS']
        data = self.read_csv(f, header=None, skiprows = self.skiprows, names=names, index_col=[0], parse_dates = True)
        return data

    def get_parameters(self, fil):
        header = self.get_header(fil)
        names = header['COLUMNS']
        units = header['UNITS']
        params = {}
        for name,unit in zip(names,units):
            params[name] = {'description' : name, 'unit': unit} 
        return params
        
if __name__ == '__main__':
    cr = CR1000()
    with open('/home/theo/acacia/data/RuweData_Loggers_v_6aug_2013/CR1000_regulated_levelcontroltable.dat') as f:
        data=cr.get_data(f)
    print data[0]
    flow = data[1]['BattV_Avg']
    print flow
