#!/usr/bin/env python
from __future__ import print_function
import os
import shutil
import subprocess
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
NEW_CONFIG_PATH = "myssl.cnf"
SSL_DIR = os.path.join(os.abspath(os.dirname(__file__)), 'ssl')
# DEFAULT_ALTNAME = "IP.1:127.0.0.1,IP.2:172.17.0.2,DNS.1:localhost,DNS.2:localhost.localdomain"
DEFAULT_REPLACE = {"fqdn": "localhost"}
DEFAULT_ALTNAME = "DNS.1:%(fqdn)s"
DEFAULT_SUBJECT = "/C=US/ST=CA/L=San Francisco/O=Mozilla/CN=%(fqdn)s"


def generate_new_ssl_conf(orig_config_string):
    """Take the original openssl.conf contents, make it readable to
    RawConfigParser, then edit it to allow for self-signed subjectAltName
    support per http://stackoverflow.com/a/21494483 .

    Returns the RawConfigParser.
    """
    config = RawConfigParser()
    # stop lowercasing key names!!
    config.optionxform = lambda option: option
    # add [default] section at the top to keep configparser from barfing
    config_string = "# Modified per http://stackoverflow.com/a/21494483\n[ default ]\n{}".format(orig_config_string)
    config.read_string(config_string)
    # print(config.sections())
    config.set(' CA_default ','copy_extensions', r'copy')  # barfs without the spaces =\
    config.set(' v3_ca ', 'subjectAltName', r'$ENV::ALTNAME')
    return config


def read_orig_ssl_conf(search_paths):
    """Find openssl.cnf and return its contents as a string
    """
    for path in search_paths:
        if os.path.exists(path):
            with open(path, "r") as fh:
                return fh.read()
    else:
        raise Exception("Can't find openssl.cnf in %s!"% search_paths)


def run_cmd(cmd):
    print("Running %s..." % cmd)
    subprocess.check_call(cmd)


def generate_keys():
    run_cmd(["openssl", "genrsa", "-out", "ssl/host.key", "3072"])  # TODO hostname
    run_cmd([
        "openssl", "req",
        "-new",
        "-x509",
        "-config", NEW_CONFIG_PATH,
        "-key", "ssl/host.key",  # TODO hostname
        "-sha256",
        "-subj", DEFAULT_SUBJECT,
        "-out", "ssl/host.cert",  # TODO hostname
        "-days", "730",
    ])


def main(name=None):
    if name not in (None, '__main__'):
        return
    # TODO argparse
    config = generate_new_ssl_conf(read_orig_ssl_conf(SSL_CONFIG_PATHS))
    with open(NEW_CONFIG_PATH, 'w') as fh:
        config.write(fh)

    os.environ['ALTNAME'] = os.environ.get('ALTNAME', DEFAULT_ALTNAME % DEFAULT_REPLACE)
    for path in ("host.key", "host.cert"):
        if os.path.exists(path):
            os.remove(path)

    generate_keys()


main(name=__name__)
