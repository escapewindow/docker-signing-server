#!/bin/sh -ex
mkdir -p ssl
DOCKER_IP=`echo $DOCKER_HOST | sed -e 's,.*://\([^:]*\):.*,\1,'`
cd ssl
if [ -f myssl.cnf ] ; then
    rm -f myssl.cnf
fi
for file in /usr/local/etc/openssl/openssl.cnf /etc/ssl/openssl.cnf ; do
    if [ -f $file ] ; then
        cp $file myssl.cnf
        printf "[SAN]\nsubjectAltName=DNS:$DOCKER_IP" >> myssl.cnf
        break
    fi
done
if [ ! -f myssl.cnf ] ; then
    echo "Can't find openssl.cnf!"
    exit 1
fi
openssl req \
    -new \
    -newkey rsa:4096 \
    -days 365 \
    -nodes \
    -x509 \
    -subj "/C=US/ST=Denial/L=Springfield/O=Dis/CN=$DOCKER_IP/subjectAltName=$DOCKER_IP" \
    -reqexts SAN \
    -config myssl.cnf \
    -keyout docker.key \
    -out docker.cert
cat docker.key >> docker.cert
cp docker.key ../host.key; cp docker.cert ../host.cert
#openssl rsa -in privkey.pem -out key.pem; openssl x509 -in cert.csr -out cert.pem -req -signkey key.pem -days 1001; cat key.pem>>cert.pem
#cp key.pem ../host.key; cp cert.pem ../host.cert
