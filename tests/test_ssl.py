#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ssl.py unit tests
"""
import argparse
from contextlib import contextmanager
import os
import pytest
import shutil
import tempfile

import csrtool

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SSL_CNF = os.path.join(DATA_DIR, "ssl.cnf")

# params {{{1
ALTNAME_PARAMS = (
    (('fqdn1', 'fqdn2'), ('ip1', ), "DNS.1:fqdn1,DNS.2:fqdn2,IP.1:ip1"),
    (('host1', 'host2'), (), "DNS.1:host1,DNS.2:host2"),
)


# helpers {{{1
class Aggregator(object):
    msgs = []

    def append(self, *args, **kwargs):
        self.msgs.append([args, kwargs])


def noop(*args, **kwargs):
    assert args or kwargs or True


@contextmanager
def temp_dir():
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir)


@pytest.fixture(scope='function')
def agg():
    return Aggregator()


@pytest.fixture(scope='function')
def fake_ssl_conf():
    with open(SSL_CNF, "r") as fh:
        return fh.read()


# generate_new_ssl_conf {{{1
def test_generate_new_ssl_conf(fake_ssl_conf):
    options = argparse.Namespace()
    options.ca_dir = "CA_DIR"
    config = csrtool.generate_new_ssl_conf(options, fake_ssl_conf)
    assert config.get(' default ', 'HOME') == '.'
    assert config.get(' v3_ca ', 'subjectAltName') == r'$ENV::ALTNAME'
    assert config.get(' CA_default ', 'dir') == options.ca_dir


def test_generate_new_ssl_conf_ca(fake_ssl_conf):
    options = argparse.Namespace()
    options.ca_dir = "CA_DIR"
    config = csrtool.generate_new_ssl_conf(options, fake_ssl_conf, ca=True)
    assert config.get(' default ', 'HOME') == '.'
    assert config.has_option(' v3_ca ', 'subjectAltName') is False
    assert config.get(' CA_default ', 'dir') == options.ca_dir


# read_orig_ssl_conf {{{1
def test_read_orig_ssl_conf(fake_ssl_conf):
    val = csrtool.read_orig_ssl_conf(SSL_CNF, [])
    assert val == fake_ssl_conf


def test_missing_orig_ssl_conf(fake_ssl_conf):
    with pytest.raises(Exception):
        csrtool.read_orig_ssl_conf(None, ["x"])


# runner {{{1
def test_runner(agg):
    cmd = ['asdf', 'blah', 'secret']
    silence = {'secret': 'notsecret'}
    csrtool.runner(cmd, silence=silence, log_fn=agg.append, call=noop)
    assert "['asdf', 'blah', 'notsecret']" in agg.msgs[0][0][0]
    assert "asdf blah notsecret" in agg.msgs[1][0][0]


# build_altname {{{1
@pytest.mark.parametrize("params", ALTNAME_PARAMS)
def test_build_altname(params):
    assert csrtool.build_altname(params[0], params[1]) == params[2]


# create_ca_files {{{1
def test_create_ca_files():
    options = argparse.Namespace()
    with temp_dir() as tmp:
        options.ca_dir = tmp
        csrtool.create_ca_files(options)
        assert os.path.exists(os.path.join(tmp, "ca.db.index"))
        assert os.path.isdir(os.path.join(tmp, "ca.db.certs"))
        with open(os.path.join(tmp, "ca.db.serial"), "r") as fh:
            serial = fh.read().rstrip()
        assert serial == "01"
