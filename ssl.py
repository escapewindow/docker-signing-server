#!/usr/bin/env python
from __future__ import print_function
import os
import shutil
import sys

if sys.version_info[0] == 2:
    from ConfigParser import RawConfigParser
else:
    from configparser import RawConfigParser

SSL_CONFIG_PATHS = (
    "/usr/local/etc/openssl/openssl.cnf",
    "/usr/local/ssl/openssl.cnf",
    "/etc/ssl/openssl.cnf",
    "/usr/lib/ssl/openssl.cnf",
)
NEW_CONFIG_PATH = "aki_ssl.cnf"

for path in SSL_CONFIG_PATHS:
    if os.path.exists(path):
        with open(NEW_CONFIG_PATH, "w") as to_:
            print("# Modified per http://stackoverflow.com/a/21494483\n[ default ]", file=to_)
            with open(path, "r") as from_:
                for line in from_:
                    print(line, file=to_, end="")
        break
else:
    raise Exception("Can't find openssl.cnf!")

config = RawConfigParser()
config.optionxform = lambda option: option  # stop lowercasing key names!
config.read(NEW_CONFIG_PATH)
print(config.sections())
config.set(' CA_default ','copy_extensions', r'copy')
config.set(' v3_ca ', 'subjectAltName', r'$ENV::ALTNAME')
with open(NEW_CONFIG_PATH, 'w') as fh:
    config.write(fh)
#
#os.environ['ALTNAME'] = "IP.1:127.0.0.1,IP.2:172.17.0.2,DNS.1:localhost,DNS.2:localhost.localdomain"
#rm -f host.key host.cert docker.cert
#openssl genrsa -out host.key 3072
#openssl req -new \
#    -x509 \
#    -config ../myssl.cnf \
#    -key host.key \
#    -sha256 \
#    -subj "/C=US/ST=Denial/L=Springfield/O=Dis/CN=localhost" \
#    -out host.cert \
#    -days 730
#
#cp host.cert docker.cert
##cat host.key >> host.cert
#cp host.key host.cert docker.cert ../
