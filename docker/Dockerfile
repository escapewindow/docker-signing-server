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
    libffi-devel \
    make \
    mercurial \
    mono-core \
    mono-devel \
    nss-tools \
    openssl \
    openssl-devel \
    python-devel \
    redhat-rpm-config \
    tcl-devel \
    tk-devel \
    unzip \\
    wget \\
    zip \\
    && yum -y clean all

RUN useradd -d /home/cltsign -s /bin/bash -m cltsign

RUN mkdir /rpms
WORKDIR /rpms
# releng-puppet2, since puppetagain.pub.build.mozilla.org seems unreachable. Requires VPN
RUN wget http://10.26.48.50/repos/yum/releng/public/CentOS/6/x86_64/signmar-19.0-2.el6.x86_64.rpm
RUN wget http://10.26.48.50/repos/yum/custom/osslsigncode/x86_64/osslsigncode-1.7.1-1.el6.x86_64.rpm
RUN wget http://10.26.48.50/repos/yum/releng/public/CentOS/6/x86_64/mozilla-python27-2.7.3-1.el6.x86_64.rpm
RUN wget http://10.26.48.50/repos/yum/releng/public/CentOS/6/x86_64/mozilla-python27-virtualenv-1.7.1.2-2.el6.x86_64.rpm
RUN wget http://10.26.48.50/repos/yum/releng/public/CentOS/6/noarch/mozilla-signing-test-files-1.2-1.noarch.rpm
RUN rpm -i --force *.rpm

RUN mkdir -p /builds/signing
WORKDIR /builds/signing
COPY requirements.txt /builds/signing/
RUN /tools/python27/bin/python /tools/python27-virtualenv/bin/virtualenv signing1
RUN signing1/bin/pip install -r requirements.txt

WORKDIR /builds/signing/signing1
#RUN hg clone -r SIGNING_SERVER https://hg.mozilla.org/build/tools
RUN mkdir -p /builds/signing/signing1/tools
COPY tools /builds/signing/signing1/tools/
RUN mkdir -p /builds/signing/signed-files /builds/signing/unsigned-files /builds/signing/signing1/secrets/{cdm,gpg,jar}
COPY *.ini /builds/signing/signing1/
COPY run.sh /builds/signing/signing1/
COPY host.* /builds/signing/signing1/
COPY cdm/* /builds/signing/signing1/secrets/cdm/
COPY gpg/* /builds/signing/signing1/secrets/gpg/
COPY jar/* /builds/signing/signing1/secrets/jar/

RUN chown -R cltsign:cltsign /builds/signing
RUN chmod 0700 /builds/signing

WORKDIR /builds/signing/signing1

ENV           HOME          /home/cltsign
ENV           SHELL         /bin/bash
ENV           USER          cltsign
ENV           LOGNAME       cltsign

EXPOSE 9110

CMD ["sh", "/builds/signing/signing1/run.sh"]
