#!/bin/sh
gpg2 --no-default-keyring --secret-keyring docker/gpg/secring.gpg --keyring docker/gpg/pubring.gpg "$@"
