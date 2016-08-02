#!/bin/sh -ex
echo "This will take a while! If you want it to be faster, you can remove 'ecdh_cert' from the following line..."
rm -rf fake_ca
./csrtool.py gen_ca gen_csr sign_csr --ca-dir fake_ca --ca-pass --fqdn localhost localhost.localdomain --ip 127.0.0.1
cp ssl/localhost.cert host.cert
cp ssl/localhost.key host.key
cat <<EOF
You can now launch the docker signing server, and use fake_ca/ca.crt to verify the cert.

To enhance security, run the following (but it will take a few minutes):
    ./csrtool.py ecdh_cert --fqdn localhost
    cp ssl/localhost.cert host.cert
EOF
