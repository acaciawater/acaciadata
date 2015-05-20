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
        subject = '[Django] Email test (2)'
        message = 'Hallo,\nDeze mail komt van een acaciadata.com server en is bedoeld om de email te testen.\nGroeten, Theo'
        fromaddr = 'webmaster@acaciadata.com'
        recipients = ['theo.kleinendorst@acaciawater.com',]
        send_mail(subject, message, fromaddr, recipients)
    