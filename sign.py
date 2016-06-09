#!/usr/bin/env python
from __future__ import print_function
import base64
import logging
import os
from poster.encode import multipart_encode
import sys
import urllib
import urllib2
import requests
from urlparse import urlparse

log = logging.getLogger()

log.setLevel(logging.DEBUG)
if len(log.handlers) == 0:
    log.addHandler(logging.StreamHandler())
log.addHandler(logging.NullHandler())

sys.path.insert(0, "/src/tools/lib/python")
from signing.client import get_token
from util.file import sha1sum

file_to_sign = 'test.mar'

o = urlparse(os.environ['DOCKER_HOST'])
print(o.hostname)
parts = o.hostname.split('.')
parts[3] = "1"
slave_ip = '.'.join(parts)
print(slave_ip)

print("TOKEN")
baseurl = "https://{}:9110".format(o.hostname)
auth = base64.encodestring('user:pass').rstrip('\n')
url = '%s/token' % baseurl
data = urllib.urlencode({
    'slave_ip': slave_ip,
    'duration': 600,
})
headers = {
    'Authorization': 'Basic %s' % auth,
    'Content-Length': str(len(data)),
}
r = requests.post(url, data=data, headers=headers, verify=False)
print(r.status_code)
print(r.reason)
print(r.text)
token = r.text
with open("token", "w") as fh:
    print(token, file=fh, end="")

print("SIGNING")

baseurl = "https://{}:9110".format(o.hostname)
sha1 = sha1sum(file_to_sign)
nonce = ""
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

data = {
    'token': token,
    'sha1': sha1,
    'filename': file_to_sign,
    'nonce': nonce,
}
url = '{}/sign/gpg/{}'.format(baseurl, sha1)
files = {'filedata': open(file_to_sign, 'rb')}
r = requests.post(url, data=data, files=files, verify=False)
#    r = urllib2.Request(url, datagen, headers)
#    req = urllib2.urlopen(r)
#print(req.info()['X-Nonce'])
#with open("nonce", "wb") as fh:
#    print(req.info()['X-Nonce'], file=fh, end="")
#    print(dir(req))
print(r.status_code)
print(r.reason)
print(r.text)
