import pandas as pd
from datetime import datetime
import requests
from pytz import utc
import logging
logger = logging.getLogger(__name__)

from generator import Generator
from acacia.data.secrets import BLIK_SECRET_TOKEN_DATA

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
    
    # Request a new token every time for simplicity, because the token expires already after a week.
    def get_auth_token(self):
        data = BLIK_SECRET_TOKEN_DATA
        headers = {'content-type': 'application/json'}
        response = requests.post('https://blik.eu.auth0.com/oauth/token', data=data, headers=headers)
        response.raise_for_status()
        return response.json().get(u'access_token')
    
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
        url = kwargs.get('url', None) #'https://backend.water.bliksensing.nl/measurements/<node-ID>'
        if url is None:
            logger.error('url for download is undefined')
            return {}
        limit = kwargs.get('limit', 50000)
        stop = kwargs.get('stop', self.utc_now())
        start = kwargs.get('start', self.unix_epoch)
        if start is None:
            start = self.unix_epoch
        
        node_id = url.split('/')[-1]
        before = self.datetime_to_unix_timestamp(stop)
        after = self.datetime_to_unix_timestamp(start)
        
        filename = 'blik_node{0}limit{1}before{2}after{3}.json'.format(node_id, limit, before, after)
        content = self.blik_api_request(url, limit, before, after)
        if 'time' not in content:
            logger.debug('download() did not complete. Possibly no new data (in that case, response = []). Response from BlikSensing: ' + content)
            return {}
        result = {filename:content}
        
        callback = kwargs.get('callback', None)
        if callback is not None:
            callback(result)
        return result
    
    
    
    