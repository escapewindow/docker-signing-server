#!/bin/sh
cat host.cert host.key > ssl_test_server.cert
openssl s_server -accept 8080 -www -HTTP -cert ssl_test_server.cert
