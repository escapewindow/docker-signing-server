#!/bin/sh -ex
./ssl.py --fqdn localhost localhost.localdomain --ip 127.0.0.1 --subject "/C=US/ST=Denial/L=Springfield/O=Dis/CN=localhost" --days 730
cp ssl/localhost.cert host.cert
cp ssl/localhost.key host.key
