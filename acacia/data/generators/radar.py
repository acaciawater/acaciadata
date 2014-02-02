'''
Created on Jan 24, 2014

@author: theo
'''
import pytz
import datetime
import numpy.ma as ma
import pandas as  pd
import StringIO
from pydap.client import open_url
from django.core.files.base import ContentFile

import logging
logger = logging.getLogger(__name__)

from generator import Generator
UTC = pytz.utc
UTC2000 = UTC.localize(datetime.datetime(2000, 1, 1))

class Regenradar(Generator):
    ''' dagtotalen ophalen van nationale regenradar'''
    def __init__(self, *args, **kwargs):
        super(Regenradar,self).__init__(args,kwargs)
        self.url = 'http://opendap.nationaleregenradar.nl/thredds/dodsC/radar/TF2400_A/2000/01/01/RAD_TF2400_A_20000101000000.h5'
        self.x = 0.0
        self.y = 0.0
        self.start = datetime.date(2014,1,1)
        self.stop = datetime.date.today()
        self.init(**kwargs)

    def init(self,**kwargs):
        if 'x' in kwargs:
            self.x = float(kwargs['x'])
        if 'y' in kwargs:
            self.y = float(kwargs['y'])
        if 'start' in kwargs:
            d = kwargs['start']
            self.start = d
        if 'stop' in kwargs:
            d = kwargs['stop']
            self.stop = d
        
    def download(self, **kwargs):
        self.init(**kwargs)
        dataset = open_url(self.url)
        grid = dataset.precipitation
        data = grid.precipitation
        x0 = dataset.east[0][0]
        y0 = dataset.north[0][0]
            
        col = int((self.x - x0) / 1000)
        row = int((y0 - self.y) / 1000)
        
        time = dataset.time[:]
        t = [UTC2000 + datetime.timedelta(seconds=float(s)) for s in time]
        t1 = -1
        t2 = len(t)-1
        for index,item in enumerate(t):
            date = item.date()
            if t1 < 0 and date >= self.start:
                t1 = index
            if date >= self.stop:
                t2 = index
                break
        z = data[row,col,t1:t2].flatten()
        t = t[t1:t2]
        z = ma.masked_where(z == -9999.0, z)
        return pd.Series(z, index=t)

    def upload(self, fil, **kwargs):
        data = self.download(**kwargs)
        if data is not None:
            io = StringIO.StringIO()
            data.to_csv(io)
            fil.save(content=ContentFile(io.getvalue()))

    def get_data(self,fil):
        return pd.read_csv(fil)

    def get_parameters(self, fil):
        return  [{'name': 'neerslag', 'description' : 'dagelijkse neerslag', 'unit': 'mm/d'}]  
        
if __name__ == '__main__':
    borgsweer = Regenradar(x=263000,y=591000)
    fil = 'test.csv'
    borgsweer.upload(fil,start=datetime.date(2014,1,1))
    