#!/bin/sh -ex
mkdir -p ssl
cd ssl
if [ -f myssl.cnf ] ; then
    rm -f myssl.cnf
fi
cp ../myssl.cnf.tmpl myssl.cnf
printf "DNS.1 = 127.0.0.1\nDNS.2 = localhost\nDNS.3 = localhost.localdomain" >> myssl.cnf
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
openssl genrsa -out host.key 3072
openssl req -new \
    -config myssl.cnf \
    -x509 \
    -key host.key \
    -extensions ssl_client \
    -sha256 \
    -subj "/C=US/ST=Denial/L=Springfield/O=Dis/CN=127.0.0.1" \
    -out docker.cert \
    -days 730

cp host.cert docker.cert
cat host.key >> host.cert
cp host.key host.cert docker.cert ../
