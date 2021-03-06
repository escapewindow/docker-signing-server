#!/usr/bin/env python
"""Generate a new self-signed private key + public cert for an ssl server.
Written against homebrew OpenSSL 1.0.2h_1 on osx 10.11.6

This will contain a `CommonName` and `subjectAltName` for newer python ssl
verification.

This requires openssl installed locally.

Example usage:

./csrtool.py gen_ca --ca-pass
./csrtool.py gen_csr --fqdn localhost localhost.localdomain --ip 127.0.0.1
./csrtool.py sign_csr --ca-pass --fqdn localhost localhost.localdomain --ip 127.0.0.1
./csrtool.py ecdh_cert --fqdn localhost

Based off of:
* http://stackoverflow.com/a/21494483
* https://gist.github.com/toolness/3073310
* https://gist.github.com/irazasyed/15885b27963d146061d7
* http://stackoverflow.com/a/7770075
* http://www.wikihow.com/Be-Your-Own-Certificate-Authority
* http://grahamc.com/blog/openssl-madness-how-to-create-keys-certificate-signing-requests-authorities-and-pem-files/

An error message of `failed to update database` during `sign_csr` may indicate
the subject has been reused, which may be a no-no in production.  In dev,
you can edit CA/ca.db.index.attr to set `unique_subject = no`
"""
# imports {{{1
from __future__ import print_function
import argparse
import datetime
from getpass import getpass
import hashlib
import logging
import os
import subprocess
import sys
import tempfile

if sys.version_info[0] == 2:
    from ConfigParser import RawConfigParser
    PYTHON2 = True
else:
    from configparser import RawConfigParser
    PYTHON2 = False

# constants {{{1
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
ACTIONS = ("gen_ca", "gen_csr", "sign_csr", "ecdh_cert")

log = logging.getLogger(__name__)


# generate_new_ssl_conf {{{1
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
    if PYTHON2:
        with tempfile.TemporaryFile() as fh:
            fh.write(config_string)
            fh.seek(0)
            config.readfp(fh)
    else:
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


# read_orig_ssl_conf {{{1
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


# runner {{{1
def runner(cmd, silence=None, log_fn=log.info, call=subprocess.check_call):
    """Run a command.
    """
    silence = silence or {}
    log_cmd = []
    for item in cmd:
        if item in silence:
            log_cmd.append(silence.get(item, '********'))
        else:
            log_cmd.append(item)
    log_fn("Running %s ..." % log_cmd)
    log_fn("Copy/paste: %s" % subprocess.list2cmdline(log_cmd))
    call(cmd)


# build_altname {{{1
def build_altname(fqdns, ips):
    altname = []
    for num, val in enumerate(fqdns, start=1):
        altname.append("DNS.%d:%s" % (num, val))
    for num, val in enumerate(ips or [], start=1):
        altname.append("IP.%d:%s" % (num, val))
    return ','.join(altname)


# create_ca_files {{{1
def create_ca_files(options):
    """Create the files the CA needs.  These may be named/laid out differently
    based on the openssl.cnf used...  It would be awesome to be able to read
    an existing openssl.cnf and generate on the fly, but also hard to do
    properly.
    """
    top_dir = options.ca_dir
    os.makedirs(os.path.join(top_dir, "ca.db.certs"))
    index = os.path.join(top_dir, "ca.db.index")
    attr = os.path.join(top_dir, "ca.db.index.attr")
    serial = os.path.join(top_dir, "ca.db.serial")
    with open(index, "w") as fh:
        pass
    with open(attr, "w") as fh:
        # By default this seems to require a unique subject per cert;
        # uncomment the below to get around that
        # print("unique_subject = no", file=fh)
        pass
    with open(serial, "w") as fh:
        print("01", file=fh)


# generate_ca {{{1
def generate_ca(options, run_cmd=runner):
    """Create a new self-signed CA to sign CSRs with.
    ca.key+password should be super private; ca.crt is public and can be used
    to verify ca-signed certs.
    """
    log.info("Generating new CA in %s..." % options.ca_dir)
    # I could overwrite or move away; for now, let's force the user to nuke
    # or move
    if os.path.exists(options.ca_dir):
        log.critical(
            "%s exists! Move it away or delete it before generating CA!"
            % options.ca_dir
        )
        sys.exit(1)
    # These files are needed to use the CA
    create_ca_files(options)
    # We need a non-ALTNAME ssl conf to generate a CA.
    ca_ssl_conf = generate_new_ssl_conf(
        options,
        read_orig_ssl_conf(options.openssl_path, SSL_CONFIG_PATHS),
        ca=True
    )
    with open(options.new_ca_conf % {'ca_dir': options.ca_dir}, 'w') as fh:
        ca_ssl_conf.write(fh)
    cmd = [
        "openssl", "genrsa",
        "-des3",
        "-out", os.path.join(options.ca_dir, "ca.key"),
    ]
    silence = {}
    if options.ca_pass:
        pass_arg = "pass:%s" % options.ca_pass
        cmd.extend(["-passout", pass_arg])
        silence[pass_arg] = "pass:********"
    cmd.extend(["4096"])
    run_cmd(cmd, silence=silence)
    cmd = [
        "openssl", "req",
        "-verbose",
        "-new",
        "-key", os.path.join(options.ca_dir, "ca.key"),
        "-out", os.path.join(options.ca_dir, "ca.csr"),
        "-%s" % options.hashalg,
        "-subj", options.subject % {'fqdn': options.ca_domain},
    ]
    if options.ca_pass:
        cmd.extend(["-passin", pass_arg])
    run_cmd(cmd, silence=silence)
    cmd = ["openssl", "ca"]
    if options.ca_pass:
        cmd.extend(["-batch", "-passin", pass_arg])
    cmd.extend([
        "-config", os.path.join(options.ca_dir, "ca_ssl.cnf"),
        "-extensions", "v3_ca",
        "-out", os.path.join(options.ca_dir, "ca.crt"),
        "-keyfile", os.path.join(options.ca_dir, "ca.key"),
        "-verbose",
        "-selfsign",
        "-md", options.hashalg,
        "-days", options.ca_days,
        "-infiles", os.path.join(options.ca_dir, "ca.csr"),
    ])
    run_cmd(cmd, silence=silence)


# generate_csr {{{1
def generate_csr(options, run_cmd=runner):
    """Generate the key and csr.
    """
    log.info("Generating new CSR...")
    hostname = options.fqdn[0]
    key = os.path.join(SSL_DIR, "%s.key" % hostname)
    csr = os.path.join(SSL_DIR, "%s.csr" % hostname)
    os.environ['ALTNAME'] = build_altname(options.fqdn, options.ips)
    log.info("Using ALTNAME of '%s' ..." % os.environ['ALTNAME'])
    for path in (key, csr):
        if os.path.exists(path):
            os.remove(path)
    repl_dict = {
        'fqdn': hostname,
    }
    run_cmd(["openssl", "genrsa", "-out", key, "4096"])
    serial_txt = hostname + str(datetime.datetime.now())
    if not PYTHON2:
        serial_txt = serial_txt.encode("utf-8")
    cmd = [
        "openssl", "req",
        "-new",
        "-config", options.newconf,
        "-key", key,
        "-%s" % options.hashalg,
        "-subj", options.subject % repl_dict,
        "-out", csr,
        "-days", options.days,
        '-set_serial', '0x%s' % hashlib.md5(serial_txt).hexdigest(),
    ]
    run_cmd(cmd)
    log.info("Private key is at %s.  CSR is at %s." % (key, csr))
    return key, csr


# sign_csr {{{1
def sign_csr(options, run_cmd=runner):
    """Sign the CSR with the CA key
    """
    log.info("Signing CSR...")
    hostname = options.fqdn[0]
    csr_path = options.csr_path % {'fqdn': hostname}
    cert = os.path.join(SSL_DIR, "%s.cert" % hostname)
    os.environ['ALTNAME'] = build_altname(options.fqdn, options.ips)
    log.info("Using ALTNAME of '%s' ..." % os.environ['ALTNAME'])
    silence = {}
    cmd = [
        "openssl", "ca",
        "-batch",
        "-verbose",
        "-config", options.newconf,
        "-extensions", "v3_ca",
        "-out", cert,
        "-keyfile", os.path.join(options.ca_dir, "ca.key"),
    ]
    if options.ca_pass:
        pass_arg = "pass:%s" % options.ca_pass
        cmd.extend(["-passin", pass_arg])
        silence[pass_arg] = "pass:********"
    cmd.extend(["-infiles", csr_path])
    run_cmd(cmd, silence=silence)
    log.info("Cert is at %s" % cert)
    log.info("You can inspect the cert via `openssl x509 -text -noout -in %s`"
             % cert)


# ecdh_cert {{{1
def ecdh_cert(options, run_cmd=runner):
    """Add DH and ECDH parameters to cert
    """
    hostname = options.fqdn[0]
    cert = os.path.join(SSL_DIR, "%s.cert" % hostname)
    log.info("Adding DH and ECDH parameters to %s..." % cert)
    dhpath = os.path.join(SSL_DIR, "%s.dhparam" % hostname)
    ecpath = os.path.join(SSL_DIR, "%s.ecparam" % hostname)
    log.info(
        "Generating Diffie-Hellman file for secure SSL/TLS negotiation...")
    cmd = ["openssl", "dhparam", "4096", "-out", dhpath]
    run_cmd(cmd)
    log.info("Generating EC curve parameters...")
    cmd = ["openssl", "ecparam", "-name", "secp384r1", "-out", ecpath]
    run_cmd(cmd)
    log.info("Concatenating DH and ECDH parameters to certificate...")
    with open(cert, "a") as fh:
        for path in (dhpath, ecpath):
            with open(path, "r") as from_:
                contents = from_.read()
            print(contents, file=fh, end='')
    log.info("Updated cert is at %s" % cert)
    log.info("You can inspect the cert via `openssl x509 -text -noout -in %s`"
             % cert)


# parse_args {{{1
def parse_args(args):
    messages = []
    parser = argparse.ArgumentParser(
        description='Generate self-signed SSL cert for a host.'
    )
    parser.add_argument('actions', metavar='ACTION', choices=ACTIONS,
                        nargs='+',
                        help='Actions to run.  Choose from %s.' % (ACTIONS, ))
    parser.add_argument('--fqdn', metavar='fqdn', type=str, nargs='*',
                        help='FQDN(s) for the SSL server (first is primary)')
    parser.add_argument('--ips', metavar='X.X.X.X', type=str, nargs='+',
                        help='IP address(es) for the SSL server')
    parser.add_argument('--days', type=str, default="365",
                        help='Number of days before SSL cert expiration')
    parser.add_argument('--ca-days', type=str, default="3650",
                        help='Number of days before CA cert expiration')
    parser.add_argument('--newconf', type=str, default="myssl.cnf",
                        help='Path to write generated openssl config')
    parser.add_argument('--new_ca_conf', type=str,
                        default="%(ca_dir)s/ca_ssl.cnf",
                        help='Path to write generated openssl config')
    parser.add_argument('--openssl-path', type=str, help='Path to openssl.cnf')
    parser.add_argument('--subject', type=str, default=DEFAULT_SUBJECT,
                        help='openssl req subject')
    parser.add_argument('--ca-dir', type=str,
                        default=os.path.join(os.path.dirname(__file__), "CA"),
                        help='CA cert path')
    parser.add_argument('--ca-domain', type=str, default="mozilla.com",
                        help='CA domain')
    parser.add_argument('--hashalg', type=str, default="sha256",
                        help='Hash algorithm to use')
    parser.add_argument('--ca-pass', action='store_true',
                        help='Only prompt for CA password once')
    parser.add_argument(
        '--csr-path', type=str, help='CSR path, for sign_csr',
        default=os.path.join(SSL_DIR, "%(fqdn)s.csr")
    )
    parser.add_argument('--verbose', '-v', type=bool, help='Verbose logging')
    options = parser.parse_args(args)
    if not options.fqdn and set(
        ["gen_csr", "sign_csr", "ecdh_cert"]
    ).intersection(set(options.actions)):
        messages.append("--fqdn required when running gen_csr or sign_csr!")
    if messages:
        log.error(messages)
        sys.exit(1)
    return options


# main {{{1
def main(name=None):
    if name not in (None, '__main__'):
        return
    if len(log.handlers) == 0:
        log.addHandler(logging.StreamHandler())
    log.addHandler(logging.NullHandler())
    options = parse_args(sys.argv[1:])
    if options.verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
    if options.ca_pass:
        prompt = "CA Password: "
        if "gen_ca" in options.actions:
            prompt = "New CA Password: "
        options.ca_pass = getpass(prompt=prompt)
    if "gen_ca" in options.actions:
        generate_ca(options)
    if "gen_csr" in options.actions or "sign_csr" in options.actions:
        log.info("Generating new ssl config at %s ..." % options.newconf)
        ssl_conf = generate_new_ssl_conf(
            options,
            read_orig_ssl_conf(options.openssl_path, SSL_CONFIG_PATHS)
        )
        with open(options.newconf, 'w') as fh:
            ssl_conf.write(fh)
    if "gen_csr" in options.actions:
        generate_csr(options)
    if "sign_csr" in options.actions:
        sign_csr(options)
    if "ecdh_cert" in options.actions:
        ecdh_cert(options)
    log.warning("Done.")


main(name=__name__)
