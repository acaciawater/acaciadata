'''
Created on Jan 28, 2015

@author: theo
'''
import logging

class DatasourceAdapter(logging.LoggerAdapter):
    
    def __init__(self,logger,datasource=None):
        self.datasource = datasource
        return super(DatasourceAdapter,self).__init__(logger, datasource)
    
    def process(self, msg, kwargs):
        kwargs['extra'] = {'datasource': self.datasource}
        return (msg, kwargs)
    
