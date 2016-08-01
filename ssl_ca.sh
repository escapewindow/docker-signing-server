#!/bin/sh -ex

echo "Generating private key and CSR..."
export ALTNAME="DNS.1:localhost,DNS.2:localhost.localdomain,IP.1:127.0.0.1"
openssl genrsa -des3 -out "$1.secured.key" 4096
openssl rsa -in "$1.secured.key" -out "$1.key"
#openssl req -verbose -new -key server.apache.key -out server.apache.csr -sha256
openssl req -verbose -new -key "$1.key" -out "$1.csr" \
    -config myssl.cnf -subj "/C=US/ST=CA/L=San Francisco/O=Moco Releng/CN=$1"

#echo "Self-signing certificate..."
#openssl x509 -req -sha512 -days 365 -config myssl.cnf -in "${csr_path}"/"$1".csr -signkey \
#    "${key_path}"/"$1".key -out "${pem_path}"/"$1".pem

echo "Signing csr..."
#openssl x509 -req -sha512 -days 365 -in "${csr_path}"/"$1".csr -signkey "${key_path}"/"$1".key -out "${pem_path}"/"$1".pem
#openssl ca -batch -config ca_ssl.cnf -extensions v3_ca -out ../"$1".pem -keyfile ca.key -verbose -selfsign -md sha256 -enddate 30170228000000Z -infiles ../"$1".csr
openssl ca -verbose -config myssl.cnf -extensions v3_ca -out "$1.pem" -keyfile CA/ca.key -infiles "$1.csr"
#openssl ca -batch -config myssl.cnf -extensions v3_ca -out "${pem_path}"/"$1".pem -keyfile "${key_path}"/"$1".key -verbose -selfsign -md sha256 -enddate 20170228000000Z -infiles "${csr_path}"/"$1".csr
echo $?
exit 0
echo "Generating Diffie-Hellman file for secure SSL/TLS negotiation..."
openssl dhparam 4096 -out "${dh_path}"/"$1".pem

echo "Generating EC curve parameters..."
openssl ecparam -name secp384r1 -out "${ecdh_path}"/"$1".pem

echo "Concatenating DH and ECDH parameters to certificate..."
cat "${dh_path}"/"$1".pem >> "${pem_path}"/"$1".pem
cat "${ecdh_path}"/"$1".pem >> "${pem_path}"/"$1".pem
