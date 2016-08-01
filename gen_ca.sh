#!/bin/sh -ex
pushd CA
openssl genrsa -des3 -out ca.key 4096
openssl req -verbose -new -key ca.key -out ca.csr -sha256 -subj "/C=US/ST=CA/L=San Francisco/O=Moco Releng/CN=mozilla.com"
openssl ca -config ca_ssl.cnf -extensions v3_ca -out ca.crt -keyfile ca.key -verbose -selfsign -md sha256 -enddate 330630235959Z -infiles ca.csr
popd
