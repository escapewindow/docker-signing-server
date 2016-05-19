# Based on https://github.com/docker-library/python/commit/9d2859cc4bd5c228cccfac2d0b515b83da93bbf2
FROM buildpack-deps

RUN apt-get update \
        && apt-get install -y curl procps mercurial libevent libevent-dev gnupg

# signing_test_files
# signmar
# include packages::mono
# include packages::openssl
# include packages::nss_tools
# include packages::jdk17
# include packages::gcc
# include packages::make
# include packages::mozilla::osslsigncode
#
# $compiler_req = Class['packages::gcc']


# remove several traces of debian python
RUN apt-get purge -y python python-minimal python2.7-minimal

ADD . /code
WORKDIR /code/Python-2.7.3
RUN ./configure \
       && make -j$(nproc) \
       && make -j$(nproc) EXTRATESTOPTS='--exclude test_file2k' test \
       && make install

WORKDIR /code
RUN hg clone https://hg.mozilla.org/build/tools

CMD ["python2"]
