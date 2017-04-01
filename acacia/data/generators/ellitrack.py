'''
Created on Mar 30, 2017

@author: theo
'''
from acacia.data.generators.generic import GenericCSV

class ElliTrack(GenericCSV):
    def __init__(self,*args,**kwargs):
        kwargs['separator'] = '\t'
        return super(ElliTrack,self).__init__(*args,**kwargs)