'''
Created on Mar 30, 2017

@author: theo
'''
from acacia.data.generators.generic import GenericCSV

class ElliTrack(GenericCSV):
    def __init__(self,*args,**kwargs):
        kwargs['separator'] = '\t'
        return super(ElliTrack,self).__init__(*args,**kwargs)
    
    def get_data(self, f, **kwargs):
        data = GenericCSV.get_data(self, f, **kwargs)
        if data is not None:
            if 'Waterstand' in data:
                data['Waterstand'] = data['Waterstand'] / 100
        return data
