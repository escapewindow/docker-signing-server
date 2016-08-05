docker-signing-server
---------------------

An attempt to create a dep signing server container for testing/development (currently gpg only)

The gpg key is throwaway; don't depend on it anywhere :)

Usage:

```bash
# Generate ssl certs
./ssl.sh
# build docker image and run. this example is interactive
(cd docker; docker build -t signingserver .); docker run -i -p 9110:9110 signingserver bash -il)
./run.sh
# In the docker terminal, you can tail signing.log to debug
# In a separate terminal, figure out how to set `my_ip`:
docker network inspect bridge
# You probably want to set `my_ip` to the subnet, but .1, e.g. 172.17.0.1
# you should be able to sign against this server using 127.0.0.1:9110
# see github.com/escapewindow/signingscript
# verify the signature
./gpg.sh --verify SIGNED_FILE
