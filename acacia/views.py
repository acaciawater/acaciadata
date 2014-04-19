from django.shortcuts import render_to_response
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
