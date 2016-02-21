from django.shortcuts import HttpResponse
from .models import Event
from .messenger import Messenger
from django.utils import timezone
import json, datetime

def testevent(request, pk):
    evt = Event.objects.get(pk=pk)
    history = evt.history_set.filter(sent=True).order_by('-date')
    start = history[0].date if history else datetime.datetime(2016,1,1,tzinfo=timezone.get_default_timezone())
    data = evt.trigger.select(start=start)
    num = data.count()
    if num > 0:
        with Messenger(evt) as m:
            for date,value in data.iteritems():
                m.add(evt.format_message(date,value,html=True))
            msg = 'Event {evt} was triggered {count} times for {ser} since {date}'.format(evt=str(evt.trigger), count=num, ser=str(evt.trigger.series),date=start)
    else:
        msg = 'No events occurred since {date}'.format(date=start)
    return HttpResponse(json.dumps(msg), content_type='application/json')

