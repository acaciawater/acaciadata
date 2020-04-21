from datetime import datetime
import logging
import re

from django.conf import settings
from pytz import utc
import requests

from generator import Generator
import pandas as pd

logger = logging.getLogger(__name__)


class Blik(Generator):
    def get_data(self, fil, **kwargs):
        fil.seek(0)
        df = pd.read_json(fil)
        df.index=df['time'].apply(lambda x: datetime.fromtimestamp(x,utc))
        return df.drop('time',axis=1)
    
    def get_parameters(self, fil):
        df = self.get_data(fil)
        params = {col:{'description':col,'unit':'-'} for col in df.columns}
        return params
    
    def request_new_token(self):
        data = settings.BLIK_SECRET_TOKEN_DATA
        headers = {'content-type': 'application/json'}
        response = requests.post('https://blik.eu.auth0.com/oauth/token', data=data, headers=headers)
        response.raise_for_status()
        Blik.token = response.json().get(u'access_token')
        now = self.datetime_to_unix_timestamp(self.utc_now())
        Blik.expire = now + response.json().get(u'expires_in')
    
    token = u''     # Store the received token in the class.
    expire = 0      # Expiration date of the token as a unix timestamp.
    def get_auth_token(self):
        now = self.datetime_to_unix_timestamp(self.utc_now())
        hour_before_expiration = Blik.expire-3600
        if (now > hour_before_expiration):
            self.request_new_token()
        return Blik.token
    
    def blik_api_request(self, url, limit, before, after):
        url = url + '?limit={0}&before={1}&after={2}'.format(limit, before, after)
        token = self.get_auth_token()
        auth_string = 'Bearer ' + token
        headers = {'authorization': auth_string}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text

    unix_epoch = datetime(1970, 1, 1, tzinfo=utc)
        
    def utc_now(self):
        now = datetime.utcnow()
        return utc.localize(now)
    
    def datetime_to_unix_timestamp(self,dt):
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = utc.localize(dt)
        return int((dt - self.unix_epoch).total_seconds())
      
    def download(self, **kwargs):
        url = kwargs.get('url', 'https://backend.water.bliksensing.nl/locations/{id}/measurements')
        if url is None:
            logger.error('url for download is undefined')
            return {}
        if '{id}' in url:
            # substitute blik location id
            blik_id = kwargs.get('blik_id')
            if blik_id is None:
                logger.error('Bliksensing location id is undefined')
                return {}
            url = url.format(id=blik_id)
        else:
            # extract location id from url
            match = re.search('locations/(\d+)/measurements',url)
            blik_id = match.groups(1) if match else 'undefined'
            
        limit = kwargs.get('limit', 50000)
        stop = kwargs.get('stop', self.utc_now())
        start = kwargs.get('start', self.unix_epoch)
        if start is None:
            start = self.unix_epoch
        
        before = self.datetime_to_unix_timestamp(stop)
        after = self.datetime_to_unix_timestamp(start)
        
        filename = 'blik_{0}limit{1}before{2}after{3}.json'.format(blik_id, limit, before, after)
        content = self.blik_api_request(url, limit, before, after)
        if 'time' not in content:
            logger.debug('download() did not complete. Possibly no new data (in that case, response = []). Response from BlikSensing: ' + content)
            return {}
        result = {filename:content}
        
        callback = kwargs.get('callback', None)
        if callback is not None:
            callback(result)
        return result
    
    
    
    