import os, urllib2, cgi
import re
import acacia.data.util as util

def spliturl(url):
    pattern = r'^(?P<scheme>ftp|https?)://(?:(?P<user>\w+)?(?::(?P<passwd>\S+))?@)?(?P<url>.+)'
    try:
        m = re.match(pattern, url)
        return m.groups()
    except:
        return ()

class Generator(object):

    def __init__(self,**kwargs):
        pass

    def get_header(self,fil):
        return {}

    def get_data(self,fil,**kwargs):
        return []
    
    def download(self, **kwargs):
        filename = kwargs.get('filename', None)
        content = ''
        result = {}
        if 'url' in kwargs:
            url = kwargs['url']
            scheme, username, passwd, path = spliturl(url)
            username = kwargs.get('username',None) or username
            passwd = kwargs.get('password',None) or passwd
            ftp = scheme == 'ftp'
            if ftp:
                if username != '':
                    if passwd != '':
                        url = 'ftp://%s:%s@%s' % (username, passwd, path)
                    else:
                        url = 'ftp://%s@%s' % (username, path)
            else:
                passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
                passman.add_password(None, url, username, passwd)
                authhandler = urllib2.HTTPBasicAuthHandler(passman)
                opener = urllib2.build_opener(authhandler)
                urllib2.install_opener(opener)

            response = urllib2.urlopen(url)
            if response is None:
                return None
            if ftp:
                # check for directory listing
                content = response.read()
                if util.is_dirlist(content):
                    # download all files in directory listing
                    dirlist = util.get_dirlist(content)
                    filenames = [f['file'] for f in dirlist]
                    for filename in filenames:
                        urlfile = url + '/' + filename
                        response = urllib2.urlopen(urlfile)
                        result[filename] = response.read()
                else:
                    filename = filename or os.path.basename(url)
                    result[filename] = content
            else:
                _,params = cgi.parse_header(response.headers.get('Content-Disposition',''))
                filename = filename or params.get('filename','file.txt')
                result[filename] = response.read()
        return result

    def get_parameters(self,fil):
        ''' return dict of all parameters in the datafile '''
        return {}
