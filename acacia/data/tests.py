"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from acacia.data.models import DataFile

class TestProvider(TestCase):
    def test_knmi(self):
        df = DataFile.objects.get(pk=1)
        df.update()
        assert(True)
        
