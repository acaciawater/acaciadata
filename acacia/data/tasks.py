from __future__ import absolute_import
from celery.utils.log import get_task_logger
from celery import shared_task
from django.shortcuts import get_object_or_404
logger = get_task_logger(__name__)
from .models import MeetLocatie, Series, Datasource
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
def update_series(pk, start = None):
    series = Series.objects.get(pk=pk)
    series.update(start=start)
    
@shared_task
def download_datasource(pk, start = None):
    datasource = Datasource.objects.get(pk=pk)
    return datasource.download(start=start)

@shared_task
def update_series_thumbnail(pk):
    series = Series.objects.get(pk=pk)
    series.make_thumbnail()
    series.save()

@shared_task
def update_datasource(pk, download = True, replace = False, calc = False):
    command = update.Command()
    command.execute(pk=pk,down=download,replace=replace,calc=calc)
    
@shared_task
def test():
    print 'test task started'
    return 'test task finished'
