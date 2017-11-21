# -*- coding: utf-8 -*-

from django.test import TestCase
from acacia.data.models import Generator
from datetime import datetime
import pytz, time, StringIO
import pandas as pd

class BlikGeneratorTests(TestCase):
    def create_generator(self):
        generator = Generator.objects.create(name=u'Generator', classname=u'acacia.data.generators.bliksensing.Blik')
        generator_class = generator.get_class()
        return generator_class()
    
    
    
    ###
    ### Tests
    ###
    
    def test_that_generator_can_be_found(self):
        gen = self.create_generator()
        self.assertEqual(str(type(gen)),u"<class 'acacia.data.generators.bliksensing.Blik'>")
       
    ###    
    ### NOTE TO SELF: The following two tests should probably be moved into the project code, so that every Datasource
    ### can test itself (all urls in the database should be automatically testable). The tests in this file can then
    ### refer to the project code. Note that these tests do not only test our own codebase, but also external stuff.
    ###
        
    def test_that_generator_can_download_something_of_expected_format(self):
        gen = self.create_generator()
        result = gen.download(url=u'https://backend.water.bliksensing.nl/measurements/9', limit=2)
        content_as_string = unicode(result.values()[0])
        self.assertTrue(len(content_as_string) > 0)
        self.assertTrue(u'time' in content_as_string)
        df = pd.read_json(content_as_string)
        self.assertTrue(u'time' in df.columns)
        self.assertTrue(len(df.columns) > 1)
        
    def test_that_the_data_received_is_recent(self):
        gen = self.create_generator()
        result = gen.download(url=u'https://backend.water.bliksensing.nl/measurements/9', limit=1)
        content_as_string = unicode(result.values()[0])
        df = pd.read_json(content_as_string)
        timestamp_latest_datapoint = df.iloc[0][u'time']
        timestamp_now = time.time()
        max_allowed_time_difference = 24.0*60.0*60.0     #24 hours in seconds
        self.assertTrue(timestamp_now - timestamp_latest_datapoint < max_allowed_time_difference)
        
    def test_download_options_start_stop_limit(self):
        gen = self.create_generator()
        stop = pytz.timezone(u'Europe/Amsterdam').localize(datetime(2017, 11, 11, 0, 0, 0))
        result = gen.download(url=u'https://backend.water.bliksensing.nl/measurements/9', limit=1, start=None, stop=stop)
        self.assertEqual(result.keys()[0],u'blik_node9limit1before1510354800after0.json')
        self.assertTrue(result.values()[0].count(u'time') <= 1)
        
    def test_get_data(self):
        gen = self.create_generator()
        contents = u'[{"time":1510824554.000000000,"air_Pa":102255,"air_K":282.247,"water_Pa":109513,"water_K":285.51,"water_m":-0.809},{"time":1510825454.000000000,"air_Pa":102255,"air_K":282.353,"water_Pa":109517,"water_K":285.51,"water_m":-0.809}]'
        mock_file = StringIO.StringIO(contents)
        df = gen.get_data(mock_file)
        mock_file.close()
        data = {u'air_K':[282.247,282.353], u'air_Pa':[102255,102255], u'water_K':[285.51,285.51], u'water_Pa':[109513,109517], u'water_m':[-0.809,-0.809]}
        index = pd.Index([datetime.fromtimestamp(1510824554,pytz.utc),datetime.fromtimestamp(1510825454,pytz.utc)], name=u'time')
        expected_df = pd.DataFrame(data=data, index=index)
        pd.util.testing.assert_frame_equal(df, expected_df)
        
    def test_get_parameters(self):
        gen = self.create_generator()
        contents = u'[{"time":1510824554.000000000,"air_Pa":102255,"air_K":282.247,"water_Pa":109513,"water_K":285.51,"water_m":-0.809},{"time":1510825454.000000000,"air_Pa":102255,"air_K":282.353,"water_Pa":109517,"water_K":285.51,"water_m":-0.809}]'
        mock_file = StringIO.StringIO(contents)
        params = gen.get_parameters(mock_file)
        mock_file.close()
        expected_params = {u'water_K': {'description': u'water_K', 'unit': '-'}, u'water_m': {'description': u'water_m', 'unit': '-'}, u'air_Pa': {'description': u'air_Pa', 'unit': '-'}, u'water_Pa': {'description': u'water_Pa', 'unit': '-'}, u'air_K': {'description': u'air_K', 'unit': '-'}}
        self.assertEqual(params,expected_params)
        
    def test_token_expiration(self):
        gen = self.create_generator()
        # Reset the Blik class:
        gen.__class__.token = u''
        gen.__class__.expire = 0
        
        first_token = gen.get_auth_token()
        self.assertNotEqual(gen.__class__.token,u'')
        # Sleep so that the authorization server returns a different token:
        time.sleep(0.5)
        second_token = gen.get_auth_token()
        self.assertEqual(first_token,second_token)
        #Token expires in 10 minutes and we expect a new token is fetched if the token expires within an hour.
        gen.__class__.expire = int(time.time()) + 600
        time.sleep(0.5)
        third_token = gen.get_auth_token()
        self.assertNotEqual(first_token,third_token)
        
