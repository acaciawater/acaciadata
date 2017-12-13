'''
Created on May 18, 2014

@author: theo
'''
from django.core.management.base import BaseCommand
from django.core.mail import send_mail

class Command(BaseCommand):
    args = ''
    help = 'Check email functionality'

    def handle(self, *args, **options):
        subject = 'Re: Prins Hendrik Zanddijk'
        message = 'Goedendag,\nDeze mail komt van de phzdmeet.nl server (Reverse DNS=phzdmeet.nl) en is bedoeld om de email te testen.\nVriendelijke groet, Theo'
        fromaddr = 'webmaster@phzdmeet.nl'
        recipients = ['tkleinen@gmail.com','theo.kleinendorst@acaciawater.com','t.kleinendorst@online.nl']
        send_mail(subject, message, fromaddr, recipients)
    