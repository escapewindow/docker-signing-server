# Based on https://github.com/docker-library/python/commit/9d2859cc4bd5c228cccfac2d0b515b83da93bbf2
FROM buildpack-deps

RUN apt-get update \
        && apt-get install -y curl procps gcc gnupg openssl

# signing_test_files
# signmar
# include packages::mono
# include packages::nss_tools
# libevent, libevent-dev
# include packages::jdk17
# include packages::make
# include packages::mozilla::osslsigncode


# remove several traces of debian python
RUN apt-get purge -y python python-minimal python2.7-minimal

RUN mkdir /code
COPY py273.tgz /code/
WORKDIR /
RUN tar zxvf /code/py273.tgz
WORKDIR /code/Python-2.7.3
RUN ./configure \
       && make -j$(nproc) \
#       && make -j$(nproc) EXTRATESTOPTS='--exclude test_file2k' test \
       && make install

WORKDIR /code

CMD ["python2"]
