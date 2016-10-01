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
from acacia.data.models import MeetLocatie

class HNKWater(Generator):

    def __init__(self,*args,**kwargs):
        #self.url = kwargs.get('url','http://hnk-water.nl/dl/?dl_parm={parm}&dl_coord=rd')
        self.parm = kwargs.get('parameter','GELDHD')
        return Generator.__init__(self,*args,**kwargs)
        
    def get_parameters(self, fil):
        params = {}
        for p in [p for p in ijson.items(fil,'features.item.properties')]:
            code = p['Parametercode']
            if not code in params:
                for d in p['data']:
                    params[code]={'description':p['Parameteromschrijving'],'unit':d['Eenheid']}
                    break
        return params
        #return {self.parm:{'description': 'Geleidbaarheid', 'unit': 'mS/cm'}}
    
    def download(self, **kwargs):
        url = kwargs.get('url')
        parm = kwargs.get('parameter',self.parm)
        try:
            start=kwargs.get('sjaar',2015)
            kwargs['url'] = url.format(parm=parm,start=start)
        except:
            pass
        if not 'filename' in kwargs:
            kwargs['filename'] = 'hnkwater_{}.json'.format(datetime.date.today())
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

    def get_data(self, fil, **kwargs):
        '''iterates over file and returns dataframe for parameter and location'''
        datapoints=[]
        mcode = kwargs.get('meetlocatie',None)
        pcode = kwargs.get('parameter',self.parm)
        if mcode and isinstance(mcode, MeetLocatie):
            mcode = mcode.name
            
        for p in ijson.items(fil,'features.item.properties'):
            if p['Meetpuntcode'] == mcode:
                for d in p['data']:
                    try:
                        val = float(d['Waarde'])
                        dat = datetime.datetime.strptime(d['datum'],'%Y-%m-%d')
                        # TODO: check unit
                        datapoints.append((dat,val))
                    except:
                        # problem with datapoint
                        pass
            elif datapoints:
                # different location. Assume datapoints are grouped by location, so no more points in this file
                break
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
        print gen.get_parameters(f)
        print gen.get_locations(f)
        print gen.get_data(f,meetlocatie='001010')
        
#     result = gen.download(url=defurl)
#     for key,contents in result.items():
#         print gen.get_data(StringIO.StringIO(contents))
        