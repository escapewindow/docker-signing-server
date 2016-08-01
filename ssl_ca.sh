#!/bin/sh -ex

echo "Generating private key and CSR..."
export ALTNAME="DNS.1:localhost,DNS.2:localhost.localdomain,IP.1:127.0.0.1"
openssl genrsa -des3 -out "ssl/localhost.secured.key" 4096
openssl rsa -in "ssl/localhost.secured.key" -out "ssl/localhost.key"
#openssl req -verbose -new -key server.apache.key -out server.apache.csr -sha256
openssl req -verbose -new -key "ssl/localhost.key" -out "ssl/localhost.csr" \
    -config myssl.cnf -subj "/C=US/ST=CA/L=San Francisco/O=Moco Releng/CN=localhost"

#echo "Self-signing certificate..."
#openssl x509 -req -sha512 -days 365 -config myssl.cnf -in "${csr_path}"/"localhost".csr -signkey \
#    "${key_path}"/"localhost".key -out "${cert_path}"/"localhost".cert

echo "Signing csr..."
#openssl x509 -req -sha512 -days 365 -in "${csr_path}"/"localhost".csr -signkey "${key_path}"/"localhost".key -out "${cert_path}"/"localhost".cert
#openssl ca -batch -config ca_ssl.cnf -extensions v3_ca -out ../"localhost".cert -keyfile ca.key -verbose -selfsign -md sha256 -enddate 30170228000000Z -infiles ../"localhost".csr
openssl ca -batch -verbose -config myssl.cnf -extensions v3_ca -out "ssl/localhost.cert" -keyfile CA/ca.key -infiles "ssl/localhost.csr"
#openssl ca -batch -config myssl.cnf -extensions v3_ca -out "${cert_path}"/"localhost".cert -keyfile "${key_path}"/"localhost".key -verbose -selfsign -md sha256 -enddate 20170228000000Z -infiles "${csr_path}"/"localhost".csr

exit 0
echo "Generating Diffie-Hellman file for secure SSL/TLS negotiation..."
openssl dhparam 4096 -out "ssl/localhost.dhparam"

echo "Generating EC curve parameters..."
openssl ecparam -name secp384r1 -out "ssl/localhost.ecparam"

echo "Concatenating DH and ECDH parameters to certificate..."
cat "ssl/localhost.dhparam" >> "ssl/localhost.cert"
cat "ssl/localhost.ecparam" >> "ssl/localhost.cert"
