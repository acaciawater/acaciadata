from __future__ import absolute_import
from celery.utils.log import get_task_logger
from celery import shared_task
from django.shortcuts import get_object_or_404
logger = get_task_logger(__name__)
from .models import MeetLocatie

@shared_task
def update_meetlocatie(pk):
    loc = get_object_or_404(MeetLocatie,pk=pk)
    for d in loc.datasources.all():
        num = d.download()
        if num > 0:
            data = d.get_data()
            d.update_parameters(data)
            for p in d.parameter_set.all():
                for s in p.series_set.all():
                    s.update(data)

@shared_task
def test():
    print 'test task started'
    return 'test task finished'
