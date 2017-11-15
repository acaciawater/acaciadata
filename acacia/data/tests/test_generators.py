# -*- coding: utf-8 -*-

from django.test import TestCase
from acacia.data.models import Generator
from datetime import datetime
import pytz

class BlikGeneratorTests(TestCase):
    def test_that_generator_can_be_found(self):
        generator = Generator.objects.create(name=u'Generator', classname=u'acacia.data.generators.bliksensing.Blik')
        generator_class = generator.get_class()
        gen = generator_class()
        self.assertEqual(str(type(gen)),u"<class 'acacia.data.generators.bliksensing.Blik'>")
        
    def test_that_generator_can_download_something(self):
        generator = Generator.objects.create(name=u'Generator', classname=u'acacia.data.generators.bliksensing.Blik')
        generator_class = generator.get_class()
        gen = generator_class()
        result = gen.download(url=u'https://backend.water.bliksensing.nl/measurements/9', limit=2)
        content_as_string = unicode(result.values()[0])
        self.assertTrue(u'water' in content_as_string)
        
    def test_download_options_start_stop_limit(self):
        generator = Generator.objects.create(name=u'Generator', classname=u'acacia.data.generators.bliksensing.Blik')
        generator_class = generator.get_class()
        gen = generator_class()
        
        stop = pytz.timezone(u'Europe/Amsterdam').localize(datetime(2017, 11, 11, 0, 0, 0))
        result = gen.download(url=u'https://backend.water.bliksensing.nl/measurements/9', limit=2, start=None, stop=stop)
        self.assertEqual(result.keys()[0],u'blik_node9limit2before1510354800after0.json')
        self.assertTrue(result.values()[0].count(u'time') <= 2)
        
        
        
        
        
    #TO DO   
    def test_get_parameters(self):
        self.assertEqual(True,False)
        
    def test_get_data(self):
        self.assertEqual(True,False)