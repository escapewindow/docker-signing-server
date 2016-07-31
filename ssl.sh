#!/bin/sh -ex
mkdir -p ssl
cd ssl
export ALTNAME="IP.1:127.0.0.1,DNS.1:localhost,DNS.2:localhost.localdomain"
#openssl req \
#    -new \
#    -newkey rsa:4096 \
#    -days 730 \
#    -nodes \
#    -x509 \
#    -subj "/C=US/ST=Denial/L=Springfield/O=Dis/CN=localhost" \
#    -config myssl.cnf \
#    -keyout host.key \
#    -out host.cert
#openssl rsa -in privkey.pem -out key.pem; openssl x509 -in cert.csr -out cert.pem -req -signkey key.pem -days 1001; cat key.pem>>cert.pem
#cp key.pem ../host.key; cp cert.pem ../host.cert
#
rm -f host.key host.cert docker.cert
openssl genrsa -out host.key 3072
openssl req -new \
    -x509 \
    -config ../myssl.cnf \
    -key host.key \
    -sha256 \
    -subj "/C=US/ST=Denial/L=Springfield/O=Dis/CN=localhost" \
    -out host.cert \
    -days 730

cp host.cert docker.cert
#cat host.key >> host.cert
cp host.key host.cert docker.cert ../
