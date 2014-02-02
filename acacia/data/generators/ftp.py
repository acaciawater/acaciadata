'''
Created on Jan 27, 2014

@author: theo
'''

def download(ftp,directory,file):
    ftp.cwd(directory)
    f = open(file,"wb")
    ftp.retrbinary("RETR " + file,f.write)
    f.close()
    
#import ftplib
#ftp = ftplib.FTP("ftp.domain.com")
#ftp.login("username", "password")
#download(ftp, "/www/path/to/file/", "file.ext")

class FTPProvider(object):

    def __init__(self, params):
        '''
        Constructor
        '''
        