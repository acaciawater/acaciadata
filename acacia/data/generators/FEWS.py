import logging
from generator import Generator
import ijson.backends.yajl2_cffi as ijson
import requests
import six
import pytz
import datetime, time
import pandas as pd
from django.conf import settings
from django.utils.text import slugify
from urllib import urlencode
from acacia.data import util
from acacia.data.models import MeetLocatie, Parameter
from pandas.util.testing import isiterable

logger = logging.getLogger(__name__)

class FEWS(Generator):
    ''' Get timeseries from FEWS Rest API json response ''' 
    
    def __init__(self,*args,**kwargs):
        super(FEWS,self).__init__(*args,**kwargs)
        self.organisation = kwargs.get('organisation', 'HHNK')
        self.parm = kwargs.get('parameter',['CL.berekend','EGVms_cm.meting', 'CL'])

    def timestamp(self, datetime=datetime.datetime.utcnow()):
        ''' return unix timestamp from datetime '''
        return int(time.mktime(datetime.timetuple())*1000)
                
    def download (self, **kwargs):
        ''' download json response from ddsc REST API 
            defaults: organisation = HHNK, start = 1/1/2015, end=today '''
         
        base_url = kwargs.get('url', None)
        if not base_url:
            logger.error('FEWS url is missing')
            return {}
        if not base_url.endswith('/'):
            base_url += '/'
            
        username = kwargs.get('username',settings.FEWSUSERNAME)
        passwd = kwargs.get('password',settings.FEWSPASSWORD)
        start = kwargs.get('start',None) or self.timestamp(datetime.datetime(2016,1,1))
        end = kwargs.get('end',None) or self.timestamp(datetime.datetime.utcnow())
        headers = {'username': username, 'password':passwd}
        result = {}
        params = {'format':'json',
                  'location__organisation__name':'HHNK',
                  'start':start,
                  'end':end}
        for pname in self.parm:
            params['name'] = pname
            url = base_url + '?' + urlencode(params)
            page=1
            while url:
                response = requests.get(url = url, headers = headers)
                filename = 'ddsc{page}_{param}.json'.format(param=slugify(pname), page=page)
                result[filename] = response.text
                url = response.json()['next']
                page += 1

        callback = kwargs.get('callback', None)
        if callback is not None:
            callback(result)        
        
        return result

    def get_data(self, f, **kwargs):
        location = kwargs.get('meetlocatie',None)
        if location and isinstance(location, MeetLocatie):
            location = location.name

        params = kwargs.get('parameter',self.parm)
        if params:
            if isinstance(params, Parameter):
                params = [params.name]
            elif isinstance(params, six.string_types):
                params = [params]
            
        # find data for location and one of the parameters (always one parameter per json file)
        dfs = {}
        for ts in ijson.items(f,'results.item'):
            pname = ts['name']
            if not pname in params:
                # only 1 parameter per file
                break
            lcode = ts['location']['organisation_code']
            if not location or lcode == location: 
                events = ts['events']
                data = []
                if events:
                    for e in events:
                        tmin = e['min']
                        tmax = e['min']
                        tgem = (tmin+tmax)/2 if (tmin and tmax) else None
                        t=e['timestamp']
                        data.append((datetime.datetime.utcfromtimestamp(t/1000),tgem))
                if data:
                    df = pd.DataFrame.from_records(data, index=['datum'], columns=['datum',pname])
                    dfs[lcode] = df
                    if location:
                        # requested for a single location
                        break
        return dfs
    
    def get_parameters(self, f):
        params = {}
        for obs in ijson.items(f,'results.item.observation_type'):
            params[obs['code']] = {'description':obs['parameter_short_display_name'], 'unit': obs['referenced_unit_short_display_name']}
            break # one single parameter per file
        return params

    def iter_locations(self, fil):
        ''' iterates over point locations and returns id, coords, description tuple'''
        for feature in ijson.items(fil,'results.item.location'):
            geom = feature['geometry']
            if geom and geom['type'] == 'Point':
                x,y,z = geom['coordinates']
                coords = [float(x),float(y)]
                mcode = feature['organisation_code']
                moms = feature['name']
                yield (mcode,coords,moms)

    def get_locations(self, fil):
        ''' returns dictionary of locations with location code as key '''
        locs = {}
        for (code,coords,oms) in self.iter_locations(fil):
            locs[code]=dict(coords=coords,description=oms,srid=util.WGS84)
        return locs
            
    