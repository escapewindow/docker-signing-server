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

#a = get_token("https://{}:9110".format(o.hostname), "new_token_auth", "token_secret", "127.0.0.1", 3600)
#print(a)

username = "new_token_auth"
password = "token_secret"
baseurl = "https://{}:9110".format(o.hostname)
auth = base64.encodestring('%s:%s' % (username, password)).rstrip('\n')
url = '%s/token' % baseurl
data = urllib.urlencode({
    'slave_ip': "127.0.0.1",
    'duration': 3600,
})
headers = {
    'Authorization': 'Basic %s' % auth,
    'Content-Length': str(len(data)),
}
r = requests.get(url, auth=(username, password), data=data, headers=headers,
                 verify=False)
print(r.status_code)
print(r.text)
#r = urllib2.Request(url, data, headers)
#return urllib2.urlopen(r).read()
