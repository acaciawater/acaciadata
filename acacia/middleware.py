from django.http import HttpResponseForbidden

def FilterHostMiddleware(get_response):
    ''' 
        implements something like:
        ALLOWED_HOSTS = ['.localhost', '192.168.1.*] 
    '''
    def middleware(request):
        allowed_hosts = set(('127.0.0.1','localhost')) 
        host = request.get_host().rsplit(':',1)[0] # remove port, if any
        if host.endswith('localhost'):
            allowed_hosts.add(host)
        if host.startswith('192.168.1.'):
            allowed_hosts.add(host)

        if host not in allowed_hosts:
            raise HttpResponseForbidden

        response = get_response(request)
        return response

    return middleware
