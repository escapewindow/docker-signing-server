#!/bin/sh
openssl s_server -accept 8080 -www -HTTP -cert host.cert
