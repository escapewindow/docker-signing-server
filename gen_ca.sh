#!/bin/sh -ex
# Generate a self-signed CA key, csr, and cert
openssl genrsa -des3 -out CA/ca.key 4096
openssl req -verbose -new -key CA/ca.key -out CA/ca.csr -sha256 -subj "/C=US/ST=CA/L=San Francisco/O=Moco Releng/CN=mozilla.com"
openssl ca -config CA/ca_ssl.cnf -extensions v3_ca -out CA/ca.crt -keyfile CA/ca.key -verbose -selfsign -md sha256 -enddate 330630235959Z -infiles CA/ca.csr
