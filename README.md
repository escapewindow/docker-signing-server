docker-signing-server
---------------------

An attempt to create a dep signing server container for testing/development (currently gpg only)

The gpg key is throwaway; don't depend on it anywhere :)

Usage:

```bash
# Make sure DOCKER_HOST is set
# Generate ssl certs
./ssl.sh
# build docker image and run. this example is interactive
docker build -t signingserver .; docker run -i -p 9110:9110 signingserver bash -il
./run.sh
# in a separate terminal with $DOCKER_HOST set, run sign.py
./sign.py
# verify the signature
./gpg.sh --verify test.mar.sig
