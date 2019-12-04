# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from acacia.meetnet.bro.models.registrationrequest import RegistrationRequest

# Create your tests here.
class TestRegister(TestCase):
    fixtures = ['test_data']
    
    def setUp(self):
        TestCase.setUp(self)
        
    def tearDown(self):
        TestCase.tearDown(self)
        
    def test_xml(self):
        ''' test creation of xml document '''
        req = RegistrationRequest.objects.first()
        xml = req.as_xml()
        print(xml)
        
    def test_register(self):
        ''' test actual registration '''
        pass