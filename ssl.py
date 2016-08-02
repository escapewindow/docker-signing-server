#!/usr/bin/env python
"""Generate a new self-signed private key + public cert for an ssl server.

This will contain a CommonName and subjectAltName for newer python ssl
verification.

This requires openssl installed locally.

Based off of:
* http://stackoverflow.com/a/21494483
* https://gist.github.com/toolness/3073310
* https://gist.github.com/irazasyed/15885b27963d146061d7
* http://stackoverflow.com/a/7770075
"""
from __future__ import print_function
import argparse
import datetime
import hashlib
import logging
import os
import subprocess
import sys

if sys.version_info[0] == 2:
    from ConfigParser import RawConfigParser
    PYTHON2 = True
else:
    from configparser import RawConfigParser
    PYTHON2 = False

SSL_CONFIG_PATHS = (
    "/usr/local/etc/openssl/openssl.cnf",
    "/usr/local/ssl/openssl.cnf",
    "/etc/ssl/openssl.cnf",
    "/usr/lib/ssl/openssl.cnf",
)
SSL_DIR = os.path.join(os.path.dirname(__file__), 'ssl')
DEFAULT_SUBJECT = os.environ.get(
    "SSL_SUBJECT", "/C=US/ST=CA/L=San Francisco/O=Moco Releng/CN=%(fqdn)s"
)
ACTIONS = ("gen_ca", "gen_csr", "sign_csr")

log = logging.getLogger(__name__)



def generate_new_ssl_conf(options, orig_config_string, ca=False):
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

    log.debug(config.sections())

    # The section names barf without the spaces =\
    # Changes for subjectAltName:
    if not ca:
        config.set(' CA_default ', 'copy_extensions', r'copy')
        config.set(' v3_ca ', 'subjectAltName', r'$ENV::ALTNAME')
    # Changes for our own CA (http://stackoverflow.com/a/7770075):
    config.set(' CA_default ', 'dir', options.ca_dir)
    config.set(' CA_default ', 'certs', '$dir')
    config.set(' CA_default ', 'new_certs_dir', '$dir/ca.db.certs')
    config.set(' CA_default ', 'database', '$dir/ca.db.index')
    config.set(' CA_default ', 'serial', '$dir/ca.db.serial')
    config.set(' CA_default ', 'RANDFILE', '$dir/ca.db.rand')
    config.set(' CA_default ', 'certificate', '$dir/ca.crt')
    config.set(' CA_default ', 'private_key', '$dir/ca.key')
    config.set(' CA_default ', 'default_days', '365')
    config.set(' CA_default ', 'default_crl_days', '30')
    config.set(' CA_default ', 'default_md', 'md5')
    config.set(' CA_default ', 'preserve', 'no')
    config.set(' CA_default ', 'policy', 'policy_anything')
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
    log.info("Running %s ..." % cmd)
    log.info("Copy/paste: %s" % subprocess.list2cmdline(cmd))
    subprocess.check_call(cmd)


def build_altname(fqdns, ips):
    altname = []
    for num, val in enumerate(fqdns, start=1):
        altname.append("DNS.%d:%s" % (num, val))
    for num, val in enumerate(ips or [], start=1):
        altname.append("IP.%d:%s" % (num, val))
    return ','.join(altname)


def generate_csr(options):
    """Generate the key and csr.
    """
    hostname = options.fqdn[0]
    key = os.path.join(SSL_DIR, "%s.key" % hostname)
    cert = os.path.join(SSL_DIR, "%s.cert" % hostname)
    os.environ['ALTNAME'] = build_altname(options.fqdn, options.ips)
    log.info("Using ALTNAME of '%s' ..." % os.environ['ALTNAME'])
    for path in (key, cert):
        if os.path.exists(path):
            os.remove(path)
    repl_dict = {
        'fqdn': hostname,
    }
    run_cmd(["openssl", "genrsa", "-out", key, "3072"])
    serial_txt = hostname + str(datetime.datetime.now())
    if not PYTHON2:
        serial_txt = serial_txt.encode("utf-8")
    cmd = [
        "openssl", "req",
        "-new",
        "-x509",
        "-config", options.newconf,
        "-key", key,
        "-sha256",
        "-subj", options.subject % repl_dict,
        "-out", cert,
        "-days", str(options.days),
        '-set_serial', '0x%s' % hashlib.md5(serial_txt).hexdigest(),
    ]
    run_cmd(cmd)
    return key, cert


def create_ca_files(options):
    top_dir = options.ca_dir
    certs_dir = os.path.join(top_dir, "ca.db.certs")
    if not os.path.exists(certs_dir):
        os.makedirs(os.path.join(top_dir, "ca.db.certs"))
    index = os.path.join(top_dir, "ca.db.index")
    attr = os.path.join(top_dir, "ca.db.index.attr")
    serial = os.path.join(top_dir, "ca.db.serial")
    if not os.path.exists(index):
        with open(index, "w") as fh:
            pass
    if not os.path.exists(attr):
        with open(attr, "w") as fh:
            print("unique_subject = no", file=fh)
    if not os.path.exists(serial):
        with open(serial, "w") as fh:
            print("01", file=fh)


def generate_ca(options):
    # We need a non-ALTNAME ssl conf to generate a CA.
    if os.path.exists(options.ca_dir):
        log.critical("%s exists! Move it away or delete it before generating CA!")
        sys.exit(1)
    create_ca_files(options)
    ca_ssl_conf = generate_new_ssl_conf(
        options,
        read_orig_ssl_conf(options.openssl_path, SSL_CONFIG_PATHS),
        ca=True
    )
    with open(options.new_ca_conf, 'w') as fh:
        ca_ssl_conf.write(fh)


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Generate self-signed SSL cert for a host.'
    )
    parser.add_argument('actions', metavar='ACTION', choices=ACTIONS,
                        nargs='+',
                        help='Actions to run.  Choose from %s.' % (ACTIONS, ))
    parser.add_argument('--fqdn', metavar='fqdn', type=str, nargs='+',
                        required=True,
                        help='FQDN(s) for the SSL server (first is primary)')
    parser.add_argument('--ips', metavar='X.X.X.X', type=str, nargs='+',
                        help='IP address(es) for the SSL server')
    parser.add_argument('--days', type=int, default=365,
                        help='Number of days before expiration')
    parser.add_argument('--newconf', type=str, default="myssl.cnf",
                        help='Path to write generated openssl config')
    parser.add_argument('--new_ca_conf', type=str, default="CA/ca_ssl.cnf",
                        help='Path to write generated openssl config')
    parser.add_argument('--openssl-path', type=str, help='Path to openssl.cnf')
    parser.add_argument('--subject', type=str, default=DEFAULT_SUBJECT,
                        help='openssl req subject')
    parser.add_argument('--ca-dir', type=str,
                        default=os.path.abspath(
                            os.path.join(os.path.dirname(__file__), "CA")
                        ),
                        help='CA cert path')
    parser.add_argument('--verbose', '-v', type=bool, help='Verbose logging')
    return parser.parse_args(args)


def main(name=None):
    if name not in (None, '__main__'):
        return
    options = parse_args(sys.argv[1:])
    if options.verbose:
        log.setLevel(logging.DEBUG)
    if len(log.handlers) == 0:
        log.addHandler(logging.StreamHandler())
    log.addHandler(logging.NullHandler())
    if "gen_ca" in options.actions:
        log.info("Generating new CA...")
        generate_ca(options)
    if "gen_csr" in options.actions or "sign_csr" in options.actions:
        log.info("Generating new ssl config...")
        ssl_conf = generate_new_ssl_conf(
            options,
            read_orig_ssl_conf(options.openssl_path, SSL_CONFIG_PATHS)
        )
        with open(options.newconf, 'w') as fh:
            ssl_conf.write(fh)
    if "gen_csr" in options.actions:
        log.info("Generating new CSR...")
        key, cert = generate_csr(options)
        log.info("Private key is at %s.  CSR is at %s." % (key, cert))
    if "sign_csr" in options.actions:
        log.info("Signing CSR...")
        log.warning("Not written yet.")
        # TODO
        sys.exit(1)
        log.info("You can inspect the cert via `openssl x509 -text -noout -in %s`"
              % cert)
    log.warning("Done.")


main(name=__name__)
