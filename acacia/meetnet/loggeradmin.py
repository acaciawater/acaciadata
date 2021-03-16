from acacia.meetnet.models import Datalogger, LoggerPos
from django.core.exceptions import MultipleObjectsReturned
from django.contrib.auth.models import User
from django.conf import settings

def create(serial, model):
    ''' create a logger '''
    return Datalogger.objects.create(serial=serial, model=model)

def create_datasource(logger, location):
    ''' create a data source for a logger/location combination '''
    admin = User.objects.filter(is_superuser=True).first()
    generator=logger.generator()
    credentials = {}
    if not generator.url:
        # use default FTP credentials
        credentials.update(url=settings.FTP_URL,
                           username=settings.FTP_USERNAME,
                           password=settings.FTP_PASSWORD)
    return logger.datasources.create(name=logger.serial,
                                     meetlocatie=location,
                                     timezone='Etc/GMT-1',
                                     user=admin,
                                     generator=generator,
                                     **credentials)

def install(logger, screen, start, depth, refpnt=None):
    ''' install a logger '''
    if not logger.datasources.exists():
        create_datasource(logger, screen.mloc)
    logger.datasources.update(autoupdate=True)
    pos = screen.loggerpos_set.create(logger=logger, start_date=start, depth=depth, refpnt=refpnt or screen.refpnt)
    pos.update_files()
    return pos

def find(logger, date, strict=True):
    ''' find out where logger is installed on a given date '''
    if date is None:
        # find current installation (stop_date is None)
        query = logger.loggerpos_set.filter(stop_date__isnull=True)
    else:
        query = logger.loggerpos_set.filter(start_date__lte=date).exclude(stop_date__lt=date)
    if strict:
        count = query.count()
        if count == 0:
            raise LoggerPos.DoesNotExist()
        elif count > 1:
            raise MultipleObjectsReturned('%(count)d loggers found, expected 1' % {'count': count})
    return query

def stop(logger, date):
    ''' stop a logger '''
    install = find(logger, date)
    install.update(stop_date=date)
    logger.datasources.update(autoupdate=False)
    return install

def start(logger, date):
    ''' start a logger '''
    install = find(logger, date)
    install.update(start_date=date)
    logger.datasources.update(autoupdate=True)
    return install

def merge(logger, screen):
    ''' merge overlapping or adjacent installations '''
    query = screen.loggerpos_set.filter(logger=logger).order_by('start_date')
    p1 = None
    changed = []
    for p in query:
        if p1 is None:
            p1 = p
        else:
            p2 = p
            if p.refpnt == p1.refpnt and p.depth == p1.depth and p.start_date.date() <= p1.end_date.date():
                if p.end_date > p1.end_date:
                    p1.end_date = p.end_date
                    p1.save()
                    changed.append(p1)
                p.delete()
            else:
                p1 = p2
    for p in changed:
        p.update_files()
    return changed

def move(logger, screen, date, **options):
    ''' move a logger to a new location '''
    try:
        curpos = stop(logger,date).first()
        curpos.update_files()
        depth = options.get('depth',curpos.depth)
        refpnt = options.get('refpnt',curpos.refpnt)
    except LoggerPos.DoesNotExist:
        # logger has not been installed before
        depth = options.get('depth')
        refpnt = options.get('refpnt',screen.refpnt)

    newpos = install(logger, screen, date, depth, refpnt)
    return curpos, newpos        
