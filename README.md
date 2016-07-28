docker-signing-server
---------------------

An attempt to create a dep signing server container for testing/development (currently gpg only)

The gpg key is throwaway; don't depend on it anywhere :)

Usage:

```bash
# Generate ssl certs
./ssl.sh
# build docker image and run. this example is interactive
docker build -t signingserver .; docker run -i -p 9110:9110 signingserver bash -il
./run.sh
### THIS IS BROKEN - in a separate terminal, run sign.py
### ./sign.py
# you should be able to sign against this server using 127.0.0.1:9110
# verify the signature
./gpg.sh --verify SIGNED_FILE
