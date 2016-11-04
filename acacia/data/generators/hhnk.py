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
from itertools import groupby

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

    def iter_data(self, fil, **kwargs):
        '''iterates over file and returns rows with location, date and parameter value'''
        from acacia.data.models import MeetLocatie, Parameter
        
        location = kwargs.get('meetlocatie',None)
        if location and isinstance(location, MeetLocatie):
            location = location.name

        parameter = kwargs.get('parameter',self.parm)
        if parameter and isinstance(parameter, Parameter):
            parameter = parameter.name
            
        for p in ijson.items(fil,'features.item.properties'):
            
            loc = p['Meetpuntcode']
            if location and loc != location:
                continue 
            
            par = p['Parametercode']
            if parameter and par != parameter:
                continue
            
            for d in p['data']:
                try:
                    val = float(d['Waarde'])
                    dat = datetime.datetime.strptime(d['datum'],'%Y-%m-%d')
                    yield (loc,par,dat,val)
                except:
                    # problem with datapoint
                    pass

    def get_data(self, fil, **kwargs):
        '''iterates over file and returns data'''
        flat = pd.DataFrame(self.iter_data(fil,**kwargs),columns=['locatie','parameter','datum','waarde'])
        locs= flat.groupby('locatie')
        dfs = {}
        for loc, df in locs:
            df=df.drop('locatie',axis=1)
            df=df.drop_duplicates()
            df=df.pivot(index='datum',columns='parameter',values='waarde')
            dfs[loc] = df
        return dfs
    
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
fname = '/home/theo/texelmeet/hhnk/media/datafiles/files/None/hnkwater_2016-11-02.json'

if __name__ == '__main__':
    gen = HNKWater()
    with open(fname) as f:
#         print gen.get_parameters(f)
#         f.seek(0)
#         print gen.get_locations(f)
#         f.seek(0)
        d = gen.get_data(f)
        for k,v in d.iteritems():
            print k,v['GELDHD']
        
#     result = gen.download(url=defurl)
#     for key,contents in result.items():
#         print gen.get_data(StringIO.StringIO(contents))
        