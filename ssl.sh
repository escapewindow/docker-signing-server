#!/bin/sh -ex
./ssl.py --fqdn localhost localhost.localdomain --ip 127.0.0.1
cp ssl/localhost.cert host.cert
cp ssl/localhost.key host.key
