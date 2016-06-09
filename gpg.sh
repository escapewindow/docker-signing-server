#!/bin/sh
gpg2 --no-default-keyring --secret-keyring gpg/secring.gpg --keyring gpg/pubring.gpg "$@"
