"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from acacia.data.models import Datasource

class TestProvider(TestCase):
    def test_knmi(self):
        df = Datasource.objects.get(pk=1)
        df.update()
        assert(True)
        
def testmail():
    from django.core.mail import send_mail
    send_mail('Onderwerp', 'Dit is het bericht', 'webmaster@acaciadata.com', ['theo.kleinendorst@acaciawater.com'])
