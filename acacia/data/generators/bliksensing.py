import pandas as pd
import numpy as np
import urllib2

from acacia.data.generators.generator import Generator

class BlikSensingGenerator(Generator):    
    def download(self, **kwargs):
        
        
        
        
        
        
        
        result = {'file.txt':unicode(dict(kwargs))}
        callback = kwargs.get('callback', None)
        if callback is not None:
            callback(result)
        return result
    
    def get_data(self, fil, **kwargs):
        #get data from the file fil
        return pd.DataFrame(np.random.randn(6,4), index=pd.date_range('20170101', periods=6), columns=list('ABCD'))

    def get_parameters(self, fil):
        #get parameters from the file fil
        return {'A': {'description' : 'description', 'unit': 'unit'}, 'B': {'description' : 'description', 'unit': 'unit'}, 'C': {'description' : 'description', 'unit': 'unit'}, 'D': {'description' : 'description', 'unit': 'unit'}}

    
    