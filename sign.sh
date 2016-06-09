#!/bin/sh -x
/src/tools/release/signing/signtool.py -H gpg:192.168.99.100:2376 -c host.cert -t token -n nonce -d output -f gpg -v test.mar
