from django.shortcuts import HttpResponse
from .messenger import process_events
from ..models import Series

def testevent(request, pk):
    series = Series.objects.get(pk=pk)
    num = process_events(series)
    return HttpResponse('{num} events triggered for {ser}'.format(num=num,ser=series))

