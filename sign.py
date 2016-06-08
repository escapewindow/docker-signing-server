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

o = urlparse(os.environ['DOCKER_HOST'])
print(o.hostname)

baseurl = "https://{}:9110".format(o.hostname)
auth = base64.encodestring('user:pass').rstrip('\n')
url = '%s/token' % baseurl
data = urllib.urlencode({
    'slave_ip': "0/0",
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

baseurl = "https://{}:9110".format(o.hostname)
url = '%s/sign' % baseurl
