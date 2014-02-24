import os, urllib2, cgi
import re

def spliturl(url):
    pattern = r'^(?P<scheme>ftp|https?)://(?:(?P<user>\w+)?(?::(?P<passwd>\S+))?@)?(?P<url>\S+)'
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
        filename = ''
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
                pattern = kwargs.get('pattern',None)
                if pattern:
                    # download all matching files
                    dirlist = response.read()
                    filenames = re.findall(pattern, dirlist)
                    for filename in filenames:
                        urlfile = url + '/' + filename
                        response = urllib2.urlopen(urlfile)
                        result[filename] = response
                else:
                    filename = os.path.basename(url)
                    result[filename] = response
            else:
                _,params = cgi.parse_header(response.headers.get('Content-Disposition',''))
                filename = params.get('filename','file.txt')
                result[filename] = response
        return result

    def get_parameters(self,fil):
        ''' return list of all parameters in the datafile '''
        return []

def example():    
    theurl = 'http://www.someserver.com/toplevelurl/somepage.htm'
    username = 'johnny'
    password = 'XXXXXX'
    # a great password
    
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    # this creates a password manager
    passman.add_password(None, theurl, username, password)
    # because we have put None at the start it will always
    # use this username/password combination for  urls
    # for which `theurl` is a super-url
    
    authhandler = urllib2.HTTPBasicAuthHandler(passman)
    # create the AuthHandler
    
    opener = urllib2.build_opener(authhandler)
    
    urllib2.install_opener(opener)
    # All calls to urllib2.urlopen will now use our handler
    # Make sure not to include the protocol in with the URL, or
    # HTTPPasswordMgrWithDefaultRealm will be very confused.
    # You must (of course) use it when fetching the page though.
    
    pagehandle = urllib2.urlopen(theurl)
    # authentication is now handled automatically for us
        
