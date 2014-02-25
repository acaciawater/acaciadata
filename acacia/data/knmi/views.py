from django.shortcuts import render_to_response
from django.template import RequestContext
from models import Station, NeerslagStation
from django.contrib.gis.geos import Point
from ..util import WGS84, RDNEW
from django.contrib.auth.decorators import login_required

@login_required
def find_stations(request):
    x = request.GET.get('x',0)
    y = request.GET.get('y',0)
    type = request.GET.get('type', 'meteo')
    target = Point(float(x),float(y), srid=WGS84)
    target.transform(RDNEW)
    if type == 'neerslag':
        stations = NeerslagStation.objects.distance(target).order_by('distance')
    else: # meteo
        stations = Station.objects.distance(target).order_by('distance')
    return render_to_response('knmi/station_list.html', {'station_type': type, 'target': target, 'stations': stations}, context_instance=RequestContext(request))