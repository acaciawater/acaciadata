'''
Created on Dec 21, 2017

@author: theo
'''
from django.conf import settings
from acacia.data.generators.generator import Generator
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import pytz
from acacia.data.models import MeetLocatie

class Munisense(Generator):

    api = 'https://wareco-water2.munisense.net/webservices/v2'    

    def get_locations(self, fil):
        return Generator.get_locations(self, fil)
    
    def download(self, **kwargs):
        api = kwargs.get('url',settings.MUNISENSE_API)
        endpoint = '/groundwaterwells/{id}/{property}/query/{start_timestamp}'
        loc = kwargs.get('meetlocatie',None)
        if not loc:
            raise ValueError('Meetlocatie not defined')
        if isinstance(loc, MeetLocatie):
            loc = loc.name
        callback = kwargs.get('callback',None)
        start = kwargs.get('start',datetime.datetime(2017,1,1).localize(pytz.utc))
        username = kwargs.get('username',settings.MUNISENSE_USERNAME)
        password = kwargs.get('password',settings.MUNISENSE_PASSWORD)
        headers = {'Accept': 'application/json' }
        url = '{api}/{endpoint}'.format(api,endpoint)
        url = url.format(id=loc,property='water_level',start_timestamp=start.isoformat())
        response = requests.get(url,headers=headers,auth=HTTPBasicAuth(username,password))
        response.raise_for_status()
        filename = kwargs.get('filename','{id}_{timestamp}.json'.format(id=loc,timestamp=start.strftime('%y%m%d%H%M')))
        result = {filename:response.text}
        if callback:
            callback(result)
        return result
    
    def get_data(self, fil, **kwargs):
        return Generator.get_data(self, fil, **kwargs)
    
    def get_parameters(self, fil):
        return Generator.get_parameters(self, fil)
    
    