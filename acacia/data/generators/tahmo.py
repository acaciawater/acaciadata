import pandas as pd
import urllib, urllib2, base64, json
from datetime import datetime, timedelta
from pytz import utc

import logging
logger = logging.getLogger(__name__)

from generator import Generator
from acacia.data.secrets import TAHMO_API_KEY, TAHMO_API_SECRET

class Tahmo(Generator):
    def get_stations(self):
        basic_auth_string = base64.encodestring('%s:%s' % (TAHMO_API_KEY, TAHMO_API_SECRET)).replace('\n', '')
        url = 'https://tahmoapi.mybluemix.net/v1/stations'
        params = {}
        encodedParams = urllib.urlencode(params)
        request = urllib2.Request(url + '?' + encodedParams)
        request.add_header("Authorization", "Basic %s" % basic_auth_string)

        try:
            response = urllib2.urlopen(request)
            decoded_response = json.loads(response.read())
            return decoded_response['stations']

        except urllib2.HTTPError, err:
            if err.code == 401:
                logger.error("Tahmo Error: Invalid API credentials")
            elif err.code == 404:
                logger.error("Tahmo Error: The API endpoint is currently unavailable")
            else:
                logger.error(err)
    
    def get_timeseries(self, url, params):
        basic_auth_string = base64.encodestring('%s:%s' % (TAHMO_API_KEY, TAHMO_API_SECRET)).replace('\n', '')
        encodedParams = urllib.urlencode(params)
        logger.debug("Tahmo params: " + encodedParams)
        request = urllib2.Request(url + '?' + encodedParams)
        request.add_header("Authorization", "Basic %s" % basic_auth_string)

        try:
            response = urllib2.urlopen(request)
            content = response.read()
            decoded_response = json.loads(content)
            if(decoded_response[u'status'] == u'success'):
                return content
            else:
                logger.error(content)
        except urllib2.HTTPError, err:
            if err.code == 401:
                logger.error("Tahmo Error: Invalid API credentials")
            elif err.code == 404:
                logger.error("Tahmo Error: The API endpoint is currently unavailable")
            else:
                logger.error(err)
        return None

    unix_epoch = datetime(1970, 1, 1, tzinfo=utc)

    def _stop(self, start):
        two_weeks_later = start + timedelta(14)
        now = utc.localize(datetime.utcnow())
        if two_weeks_later > now:
            return now
        else:
            return two_weeks_later

    def _params(self, start, stop):
        if stop:
            return {'startDate': datetime.strftime(start,'%Y-%m-%dT%H:%M'), 'endDate': datetime.strftime(stop,'%Y-%m-%dT%H:%M')}
        return {'startDate': datetime.strftime(start,'%Y-%m-%dT%H:%M')}

    def download(self, **kwargs):
        url = kwargs.get('url', None) #'https://tahmoapi.mybluemix.net/v1/timeseries/<station_id>[/hourly]'
        if url is None:
            logger.error('url for download is undefined')
            return {}
        start = kwargs.get('start', self.unix_epoch)
        if start is None:
            start = self.unix_epoch
        stop = kwargs.get('stop', None)

        params = self._params(start, stop)
        station_id = url.split('/')[5]
        filename = 'tahmo-{0}-start-{1}-stop-{2}.json'.format(station_id, str(start), str(stop))
        content = self.get_timeseries(url, params)

        if not content:
            return {}
        result = {filename:content}

        callback = kwargs.get('callback', None)
        if callback is not None:
            callback(result)
        return result

    def get_data(self, fil, **kwargs):
        content = fil.read()
        data = json.loads(content)
        df = pd.read_json(json.dumps(data['timeseries']))
        return df

    def get_parameters(self, fil):
        df = self.get_data(fil)
        params = {col:{'description':col,'unit':'-'} for col in df.columns}
        return params

