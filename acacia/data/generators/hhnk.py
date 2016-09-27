'''
Created on Sep 26, 2016

@author: theo
'''

import datetime
import json
import ijson
from acacia.data.generators.generator import Generator
from acacia.data import util
import pandas as pd

class HNKWater(Generator):

    defurl = r'http://hnk-water.nl/dl/?dl_parm={parm}&dl_coord=rd' 
    defparm = 'GELDHD'
    
    def get_default_url(self):
        return self.defurl
    
    def get_parameters(self, fil):
        return {'GELDHD':{'description': 'Geleidbaarheid', 'unit': 'mS/cm'}}
    
    def download(self, **kwargs):
        url = kwargs.get('url',self.get_default_url())
        parm = kwargs.get('parameter',self.defparm)
        try:
            kwargs['url'] = url.format(parm=parm)
        except:
            pass
        return Generator.download(self, **kwargs)
    
    def get_data1(self, fil, **kwargs):
        '''loads entire file in memory and returns dataframe for all locations'''
        o = json.load(fil)
        datapoints=[]
        for feature in o['features']:
            geom = feature['geometry']
            coords = geom['coordinates']
            prop = feature['properties']
            mcode = prop['Meetpuntcode']
            moms = prop['Meetpuntomschrijving']
            pcode = prop['Parametercode']
            poms = prop['Parameteromschrijving']
            data = prop['data']
            for d in data:
                val = float(d['Waarde'])
                dat = datetime.datetime.strptime(d['datum'],'%Y-%m-%d')
                datapoints.append((dat,mcode,val))
        df = pd.DataFrame.from_records(datapoints,index=['meetpunt','datum'],columns=['datum','meetpunt','GELDHD'])
        return df

    def get_data2(self, fil, **kwargs):
        '''iterates over entire file and returns dataframe for all locations'''
        datapoints=[]
        for prop in ijson.items(fil,'features.item.properties'):
            mcode = prop['Meetpuntcode']
            data = prop['data']
            for d in data:
                try:
                    val = float(d['Waarde'])
                    dat = datetime.datetime.strptime(d['datum'],'%Y-%m-%d')
                    datapoints.append((dat,mcode,val))
                except:
                    pass
        df = pd.DataFrame.from_records(datapoints,index=['meetpunt','datum'],columns=['datum','meetpunt','GELDHD'])
        return df

    def get_data(self, fil, **kwargs):
        '''iterates over file and returns dataframe for parameter and location'''
        datapoints=[]
        mcode = kwargs.get('meetlocatie',None)
        pcode = kwargs.get('parameter',self.defparm)
        for p in [p for p in ijson.items(fil,'features.item.properties') if p['Meetpuntcode']==mcode and p['Parametercode']==pcode]:
            for d in p['data']:
                try:
                    val = float(d['Waarde'])
                    dat = datetime.datetime.strptime(d['datum'],'%Y-%m-%d')
                    datapoints.append((dat,val))
                except:
                    # problem with datapoint
                    pass
        df = pd.DataFrame.from_records(datapoints,index=['datum'],columns=['datum',pcode])
        df.dropna(inplace=True)
        return df

    def iter_locations(self, fil):
        ''' iterates over point locations and returns id, coords, description tuple'''
        for feature in ijson.items(fil,'features.item'):
            geom = feature['geometry']
            if geom['type'] == 'Point':
                coords = geom['coordinates']
                props = feature['properties']
                mcode = props['Meetpuntcode']
                moms = props['Meetpuntomschrijving']
                yield (mcode,coords,moms)

    def get_locations(self, fil):
        ''' returns dictionary of locations with location code as key '''
        locs = {}
        for (code,coords,oms) in self.iter_locations(fil):
            locs[code]=dict(coords=coords,description=oms,srid=util.RDNEW)
        return locs
    
#from acacia.data.models import Datasource
fname = '/home/theo/texelmeet/hhnk/hnk-water.nl.json'

if __name__ == '__main__':
    gen = HNKWater()
    with open(fname) as f:
#        print gen.get_locations(f)
        print gen.get_data(f,meetlocatie='001010')
        
#     result = gen.download(url=defurl)
#     for key,contents in result.items():
#         print gen.get_data(StringIO.StringIO(contents))
        