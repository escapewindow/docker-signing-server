# Based on build-puppet 649f99991f467d1769e08a23dba7e24aac4fee39
FROM centos:centos6
MAINTAINER Aki Sasaki <aki@mozilla.com>

RUN yum -y update && yum -y install \
    curl \
    gcc \
    gnupg \
    libevent \
    libevent-devel \
    java-1.6.0-openjdk-devel \
    make \
    mercurial \
    mono-core \
    mono-devel \
    nss-tools \
    openssl \
    tcl-devel \
    tk-devel \
    wget \\
    && yum -y clean all

RUN useradd -d /home/dockersign -s /bin/bash -m dockersign

RUN mkdir /rpms
WORKDIR /rpms
RUN wget http://puppetagain.pub.build.mozilla.org/data/repos/yum/releng/public/CentOS/6/x86_64/signmar-19.0-2.el6.x86_64.rpm
RUN wget http://puppetagain.pub.build.mozilla.org/data/repos/yum/custom/osslsigncode/x86_64/osslsigncode-1.7.1-1.el6.x86_64.rpm
RUN wget http://puppetagain.pub.build.mozilla.org/data/repos/yum/releng/public/CentOS/6/x86_64/mozilla-python27-2.7.3-1.el6.x86_64.rpm
RUN wget http://puppetagain.pub.build.mozilla.org/data/repos/yum/releng/public/CentOS/6/x86_64/mozilla-python27-virtualenv-1.7.1.2-2.el6.x86_64.rpm
RUN wget http://puppetagain.pub.build.mozilla.org/data/repos/yum/releng/public/CentOS/6/noarch/mozilla-signing-test-files-1.2-1.noarch.rpm
RUN rpm -i --force *.rpm

RUN mkdir -p /builds/signing
WORKDIR /builds/signing
COPY requirements.txt /builds/signing/
RUN /tools/python27/bin/python /tools/python27-virtualenv/bin/virtualenv signing1
RUN signing1/bin/pip install -r requirements.txt

WORKDIR /builds/signing/signing1
RUN hg clone -r SIGNING_SERVER https://hg.mozilla.org/build/tools
RUN mkdir -p /builds/signing/signed-files /builds/signing/unsigned-files /builds/signing/signing1/secrets/gpg /builds/signing/signing1/secrets/signcode /builds/signing/signing1/secrets/sha2signcode
COPY *.ini /builds/signing/signing1/
COPY run.sh /builds/signing/signing1/
COPY host.* /builds/signing/signing1/
COPY gpg/* /builds/signing/signing1/secrets/gpg/
COPY signcode/* /builds/signing/signing1/secrets/signcode/
COPY signcode/* /builds/signing/signing1/secrets/sha2signcode/

RUN chown -R dockersign:dockersign /builds/signing
RUN chmod 0700 /builds/signing

WORKDIR /builds/signing/signing1

ENV           HOME          /home/dockersign
ENV           SHELL         /bin/bash
ENV           USER          dockersign
ENV           LOGNAME       dockersign

EXPOSE 9110

CMD ["sh", "/builds/signing/signing1/run.sh"]
