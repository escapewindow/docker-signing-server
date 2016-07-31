#!/usr/bin/env python
"""Generate a new self-signed private key + public cert for an ssl server.

This will contain a CommonName and subjectAltName for newer python ssl
verification.

This requires openssl installed locally.
"""
from __future__ import print_function
import argparse
import os
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
SSL_DIR = os.path.join(os.path.dirname(__file__), 'ssl')
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
    config_string = "# Modified per http://stackoverflow.com/a/21494483\n" + \
                    "[ default ]\n{}".format(orig_config_string)
    config.read_string(config_string)

    # print(config.sections())

    # The section names barf without the spaces =\
    config.set(' CA_default ', 'copy_extensions', r'copy')
    config.set(' v3_ca ', 'subjectAltName', r'$ENV::ALTNAME')
    return config


def read_orig_ssl_conf(path, search_paths):
    """Find openssl.cnf and return its contents as a string
    """
    if path is not None:
        search_paths = [path]
    for path in search_paths:
        if os.path.exists(path):
            with open(path, "r") as fh:
                return fh.read()
    else:
        raise Exception("Can't find openssl.cnf in %s!" % search_paths)


def run_cmd(cmd):
    """Run a command.
    """
    print("Running %s ..." % cmd)
    print("Copy/paste: %s" % subprocess.list2cmdline(cmd))
    subprocess.check_call(cmd)


def build_altname(fqdns, ips):
    altname = []
    for num, val in enumerate(fqdns, start=1):
        altname.append("DNS.%d:%s" % (num, val))
    for num, val in enumerate(ips or [], start=1):
        altname.append("IP.%d:%s" % (num, val))
    return ','.join(altname)


def generate_keys(options):
    """Generate the key and cert.
    """
    hostname = options.fqdn[0]
    key = os.path.join(SSL_DIR, "%s.key" % hostname)
    cert = os.path.join(SSL_DIR, "%s.cert" % hostname)
    os.environ['ALTNAME'] = build_altname(options.fqdn, options.ips)
    print("Using ALTNAME of '%s' ..." % os.environ['ALTNAME'])
    for path in (key, cert):
        if os.path.exists(path):
            os.remove(path)
    repl_dict = {
        'fqdn': hostname,
    }
    run_cmd(["openssl", "genrsa", "-out", key, "3072"])
    run_cmd([
        "openssl", "req",
        "-new",
        "-x509",
        "-config", options.newconf,
        "-key", key,
        "-sha256",
        "-subj", options.subject % repl_dict,
        "-out", cert,
        "-days", str(options.days),
    ])
    return key, cert


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Generate self-signed SSL cert for a host.'
    )
    parser.add_argument('--fqdn', metavar='fqdn', type=str, nargs='+',
                        required=True,
                        help='FQDN(s) for the SSL server (first is primary)')
    parser.add_argument('--ips', metavar='X.X.X.X', type=str, nargs='+',
                        help='IP address(es) for the SSL server')
    parser.add_argument('--days', type=int, default=365,
                        help='Number of days before expiration')
    parser.add_argument('--newconf', type=str, default="myssl.cnf",
                        help='Path to write generated openssl config')
    parser.add_argument('--openssl-path', type=str, help='Path to openssl.cnf')
    parser.add_argument('--subject', type=str, default=DEFAULT_SUBJECT,
                        help='openssl req subject')
    return parser.parse_args(args)


def main(name=None):
    if name not in (None, '__main__'):
        return
    options = parse_args(sys.argv[1:])
    ssl_conf = generate_new_ssl_conf(
        read_orig_ssl_conf(options.openssl_path, SSL_CONFIG_PATHS)
    )
    with open(options.newconf, 'w') as fh:
        ssl_conf.write(fh)
    key, cert = generate_keys(options)
    print("Private key is at %s.  Public cert is at %s." % (key, cert))
    print("You can inspect the cert via `openssl x509 -text -noout -in %s`"
          % cert)
    print("Done.")


main(name=__name__)
