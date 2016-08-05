#!/bin/sh
# Helper script to use the keys in docker/gpg/ keyrings
gpg2 --no-default-keyring --secret-keyring docker/gpg/secring.gpg --keyring docker/gpg/pubring.gpg "$@"
