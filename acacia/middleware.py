from django.http import HttpResponseForbidden
from django.conf import settings
from string import lower

def FilterHostMiddleware(get_response):
    ''' 
        implements something like:
        ALLOWED_HOSTS = ['.localhost', '192.168.1.] 
    '''
    def middleware(request):
        if hasattr(settings,'FILTER_HOSTS'):
            allowed_hosts = map(lower, settings.FILTER_HOSTS)
        else:
            allowed_hosts = ('127.0.0.1','localhost') 
        host = request.get_host().rsplit(':',1)[0].lower() # remove port, if any
        for pattern in allowed_hosts:
            if pattern in host:
                return get_response(request)
        return HttpResponseForbidden('Host not allowed.')

    return middleware
