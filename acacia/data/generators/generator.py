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
            ftp = url.startswith('ftp://')
            if 'username' in kwargs:
                username = kwargs['username']
                password = kwargs.get('password','')
                if ftp:
                    # fill in username and password ftp://username:password@domain/path
                    if password == '':
                        url = 'ftp://%s@%s' % (username, url[6:])
                    else:
                        url = 'ftp://%s:%s@%s' % (username, password, url[6:])
                    
                else:
                    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
                    passman.add_password(None, url, username, password)
                    authhandler = urllib2.HTTPBasicAuthHandler(passman)
                    opener = urllib2.build_opener(authhandler)
                    urllib2.install_opener(opener)

            response = urllib2.urlopen(url)
            if response is not None:
                if ftp:
                    filename = os.path.basename(url)
                else:
                    _,params = cgi.parse_header(response.headers.get('Content-Disposition',''))
                    filename = params.get('filename','file.txt')
                content = response.read()
        return [filename, content]

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
        
