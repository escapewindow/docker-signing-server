#!/usr/bin/env python
from __future__ import print_function
import base64
import os
import sys
import urllib
import urllib2
import requests
from urlparse import urlparse

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

print("SIGNING")

baseurl = "https://{}:9110".format(o.hostname)
url = '%s/sign/gpg' % baseurl
data = {
    'token': token,
    'sha1': sha1sum(file_to_sign),
    'filename': file_to_sign,
}
headers = {
    'Content-Length': str(len(data)),
}
with open(file_to_sign, "rb") as fh:
    data['filedata'] = fh
    r = requests.post(url, data=data, headers=headers, verify=False)
print(r.status_code)
print(r.reason)
print(r.text)
