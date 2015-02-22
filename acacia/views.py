from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext

import logging
logger = logging.getLogger(__name__)

def home(request):
    return render_to_response('home.html',context_instance=RequestContext(request))

def cam(request, how):
    if how is None:
        template = 'cam.html'
    elif how == 'stream':
        template = 'cam_stream.html' 
    return render_to_response(template,context_instance=RequestContext(request))

def mail(request):
    from django.core.mail import send_mail
    send_mail('Re: mailtest', 'Dit is verzonden door acaciadata.com', 'webmaster@acaciadata.com', ['theo.kleinendorst@acaciawater.com'], auth_user='webmaster@acaciadata.com', auth_password = 'acaciawater')
    return HttpResponse('Sending email succeeded')