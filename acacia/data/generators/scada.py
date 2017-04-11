'''
Created on Apr 11, 2017

@author: theo
'''
from acacia.data.generators.generator import Generator 

class Scada(Generator):
    def __init__(self,*args,**kwargs):
        return super(Scada,self).__init__(*args,**kwargs)
    
    def getwords(self, f):
        return [col.strip().strip("'") for col in f.readline().split(';')]

    def get_header(self, f):
        f.seek(0)
        dev = self.getwords(f)
        nrs = self.getwords(f)
        f.readline()
        names = self.getwords(f)
        numinfo = self.getwords(f)
        units = self.getwords(f)

        sections = {}
        names = ['|'.join([d,n,r]) for (d,n,r) in zip(dev,nrs,names)]
        sections['COLUMNS'] = names
        sections['UNITS'] = units
        
        return sections
            
    def get_data(self, f, **kwargs):
        header = self.get_header(f)
        columns = header['COLUMNS']
        data = self.read_csv(f, header=None, skiprows=6, names = columns, sep = ';', decimal=',', index_col = 0, parse_dates = [0], dayfirst = True)
        return data

    def get_parameters(self, fil):
        header = self.get_header(fil)
        names = header['COLUMNS'][1:]
        params = {}
        for name in names:
            params[name] = {'description' : name, 'unit': '-'} 
        return params
    
#     def get_locations(self, f):
#         f.seek(0)
#         device = [col.strip() for col in f.readline().split(';')] # device
#         deviceno = [col.strip() for col in f.readline().split(';')] # device number
#         
