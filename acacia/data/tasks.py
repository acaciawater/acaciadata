from __future__ import absolute_import
from celery.utils.log import get_task_logger
from celery import shared_task
from django.shortcuts import get_object_or_404
logger = get_task_logger(__name__)
from .models import MeetLocatie
from acacia.management.commands import update

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
def update_series(series, data = None, start = None):
    series.update(data,start)
    
@shared_task
def download_datasource(datasource, start = None):
    return datasource.download(start=start)

@shared_task
def update_parameter_thumbnail(parameter,data = None):
    parameter.make_thumbnail(data)
    parameter.save()

@shared_task
def update_series_thumbnail(series,data = None):
    series.make_thumbnail()
    series.save()

@shared_task
def update_datasource(datasource, download = True, replace = False):
    command = update.Command()
    command.handle(pk=datasource.pk,down=download,replace=replace)
    
@shared_task
def test():
    print 'test task started'
    return 'test task finished'
