#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ssl.py unit tests
"""
import argparse
import os
import pytest

import csrtool

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


@pytest.fixture(scope='function')
def fake_ssl_conf():
    with open(os.path.join(DATA_DIR, "ssl.cnf"), "r") as fh:
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
    val = csrtool.read_orig_ssl_conf(os.path.join(DATA_DIR, "ssl.cnf"), [])
    assert val == fake_ssl_conf


def test_missing_orig_ssl_conf(fake_ssl_conf):
    with pytest.raises(Exception):
        csrtool.read_orig_ssl_conf(None, ["x"])
