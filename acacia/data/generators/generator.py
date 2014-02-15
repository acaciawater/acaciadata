import os, urllib2, cgi

class Generator(object):

    def __init__(self,**kwargs):
        pass

    def get_header(self,fil):
        return {}

    def get_data(self,fil,**kwargs):
        return []
        
    def download(self, **kwargs):
        filename = ''
        content = ''
        if 'url' in kwargs:
            url = kwargs['url']
            response = urllib2.urlopen(url)
            if response is not None:
                if url.startswith('ftp'):
                    filename = os.path.basename(url)
                else:
                    _,params = cgi.parse_header(response.headers.get('Content-Disposition',''))
                    filename = params.get('filename','file.txt')
                content = response.read()
        return [filename, content]

    def get_parameters(self,fil):
        ''' return list of all parameters in the datafile '''
        return []
    