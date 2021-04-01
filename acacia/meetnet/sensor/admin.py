from acacia.meetnet.models import Datalogger, LoggerPos, Screen
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.aggregates import Min
from acacia.meetnet.util import recomp

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
                                     config = {'logger': logger.serial}
                                     **credentials)

def install(logger, screen, date, depth, refpnt=None):
    ''' install a logger '''
    # TODO: stop running logger installed in this screen
    if not logger.datasources.exists():
        create_datasource(logger, screen.mloc)
    logger.datasources.update(autoupdate=True)
    pos = screen.loggerpos_set.create(logger=logger, start_date=date, depth=depth, refpnt=refpnt or screen.refpnt)
    pos.update_files()
    return pos

def update_files(installations):
    ''' update source files of logger installations '''
    for install in installations:
        yield install, install.update_files()
    
def find_running(logger):
    return logger.loggerpos_set.filter(end_date__isnull=True)

def find_stopped(logger):
    return logger.loggerpos_set.filter(end_date__isnull=False)

def stop(logger, date):
    ''' stop a logger by setting stop_date an disable autoupdate on datasources'''
    candidates = find_running(logger).filter(start_date__lte=date)
    candidates.update(end_date=date)
    logger.datasources.update(autoupdate=False)
    update_files(candidates)
    return candidates

def start(logger, date):
    ''' start a logger by clearing stop_date and enabling autoupdate on datasources'''
    candidates = find_stopped(logger).filter(start_date__gte=date, end_date__lte=date)
    candidates.update(end_date=None)
    logger.datasources.update(autoupdate=False)
    update_files(candidates)
    return candidates

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
                if p1.end_date is None or p.end_date > p1.end_date:
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
    ''' move a logger to a new location or install as new logger '''
    try:
        # stop logger if already installed
        curpos = stop(logger,options.get('stop', date)).first()
    except LoggerPos.DoesNotExist:
        pass

    depth = options.get('depth')
    refpnt = options.get('refpnt')
    if depth == None or refpnt is None:
        installations = screen.loggerpos_set.all()
        if installations.exists():
            # use latest logger installation in this screen as default
            curpos = installations.latest('start_date')
            depth = depth or curpos.depth
            refpnt = refpnt or curpos.refpnt
    
    newpos = install(logger, screen, date, depth, refpnt)
    return curpos, newpos        


def refresh(datasource, start, stop=None):
    ''' 
    reload files from remote
    useful when something has changed on ellitrack site 
    '''
    pk = datasource.pk

    # clone datasource
    clone = datasource
    clone.id = None
    clone.pk = None
    clone.name += '_clone'
    clone.save()

    # now datasource and clone represent same instance
    # reload original datasource from db
    original = datasource._meta.model.objects.get(pk=pk)
    
    # select source files
    files = original.sourcefiles.all()
    if start:
        files = files.filter(start__gte=start)
    if stop:
        files = files.filter(stop__lte=stop)

    # move selected files from original to clone
    files.update(datasource=clone)

    try:
        # download files again
        newfiles = original.download(start)
        return newfiles
    except:
        # something went wrong while downloading
        # restore original files
        files.update(datasource=original)
        raise
    finally:
        clone.delete()
        
def refresh_loggerdata(logger, start, stop=None):
    '''
    refresh loggerdata
    yields updated time series and screen
    '''
    # fetch new datafiles from origin
    for ds in logger.datasources.all():
        refresh(ds, start, stop)

    # update installation files
    query = logger.loggerpos_set.all()
    if start:
        query = query.exclude(end_date__lt=start)
    if stop:
        query = query.exclude(start_date__gt=stop)
    
    installations = query
    
    for install in installations:
        install.update_files()
    
    # update time series
    screens = set([inst.screen for inst in installations])
    for screen in screens:
        series = screen.find_series()
        recomp(screen, series, start)
        yield series, screen
            