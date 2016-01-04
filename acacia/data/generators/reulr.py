'''
Created on Feb 22, 2014

@author: theo
'''
import re

text = 'drwxrwxr-x 6 theo theo      4096 Mar  3 14:22 acacia\r\n\
-rw-r--r-- 1 theo vboxsf 5604352 Mar  4 15:07 acaciadata.db\r\n\
-rw-rw-r-- 1 theo theo    200796 Mar  4 15:08 acacia.log\r\n\
-rw-rw-r-- 1 theo theo     94222 Mar  4 14:45 django.log\r\n\
-rw-rw-r-- 1 theo theo         0 Mar  4 15:22 space and list\r\n\
-rwxrw-r-- 1 theo theo       249 Feb  2 23:12 manage.py\r\n\
drwxrwxr-x 4 theo theo      4096 Mar  4 14:55 media\r\n\
-rw-rw-r-- 1 theo theo       546 Feb 28 00:02 requirements.txt\r\n'
#pattern = r'(?P<flags>[drwxst-]{10})\s+(?P<count>\d+)\s+(?P<user>\w+)\s+(?P<group>\w+)\s+(?P<size>\d+)\s+(?P<month>\w{3})\s+(?P<day>\d{1,2})'
#pattern = r'([drwxst-]{10})\s+(\d+)\s+(\w+)\s+(\w+)\s+(\d+)\s+(\w{3}\s+\d{1,2}\s+\d{2}:\d{2})\s+([^\r]+)'
pattern = r'(?P<flags>[drwxst-]{10})\s+(?P<count>\d+)\s+(?P<user>\w+)\s+(?P<group>\w+)\s+(?P<size>\d+)\s+(?P<date>\w{3}\s+\d{1,2}\s+\d{2}:\d{2})\s+(?P<file>[^\r]+)'
res = [m.groupdict() for m in re.finditer(pattern, text,re.MULTILINE)]
print res

#res = re.findall(pattern,text,re.MULTILINE)
#for r in res:
#    print r
#print res

m = re.match(pattern,text,re.MULTILINE)
if m is not None:
    grps = m.groups()
    for g in grps:
        print g

# text = 'blablabla (in 0.1 mm per dag)'
# pattern = r'\(in\s([^)]+)\)'
# pat = re.compile(pattern)
# m = re.search(pattern,text)
# if m is not None:
#     grps = m.groups()
#     for g in grps:
#         print g

#pattern = r'^(ftp|http)://((?P<user>\w+)\:)?(?P<passwd>\\S+)@(?P<address>\S+)'
pattern = r'^(?P<scheme>ftp|https?)://(?:(?P<user>\w+)?(?::(?P<passwd>\S+))?@)?(?P<url>.+)'
pat = re.compile(pattern)
m = pat.match('http://theo@ftp.data.com/folder/file twee.ext')
grps = m.groups()
for g in grps:
    print g

scheme= m.group('scheme')
user= m.group('user')
passwd= m.group('passwd')
url= m.group('url')
print scheme, user, passwd, url

