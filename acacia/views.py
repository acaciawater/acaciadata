from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

import logging
logger = logging.getLogger(__name__)

def home(request):
    return render_to_response('home.html',context_instance=RequestContext(request))

def cam(request):
    return render_to_response('cam.html',context_instance=RequestContext(request))

def logview(logfile, request):
    with open(logfile,"r") as f:
        resp = HttpResponse(f.read(), mimetype = "text")
        resp['Content-Type'] = 'text/csv; filename=%s' % logfile
        resp['Content-Disposition'] = 'attachment; filename=%s' % logfile
        return resp
    