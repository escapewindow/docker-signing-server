# Based on build-puppet 649f99991f467d1769e08a23dba7e24aac4fee39
FROM centos:centos6

RUN yum -y update \
        && yum -y install curl gcc gnupg make openssl libevent libevent-devel java-1.6.0-openjdk-devel mono-core mono-devel nss-tools wget mercurial tcl-devel tk-devel

RUN mkdir /builds
RUN useradd -d /home/cltsign -s /bin/bash -m cltsign
RUN mkdir /rpms
WORKDIR /rpms
RUN wget http://puppetagain.pub.build.mozilla.org/data/repos/yum/releng/public/CentOS/6/x86_64/signmar-19.0-2.el6.x86_64.rpm
RUN wget http://puppetagain.pub.build.mozilla.org/data/repos/yum/custom/osslsigncode/x86_64/osslsigncode-1.7.1-1.el6.x86_64.rpm
RUN wget http://puppetagain.pub.build.mozilla.org/data/repos/yum/releng/public/CentOS/6/x86_64/mozilla-python27-2.7.3-1.el6.x86_64.rpm
RUN wget http://puppetagain.pub.build.mozilla.org/data/repos/yum/releng/public/CentOS/6/x86_64/mozilla-python27-virtualenv-1.7.1.2-2.el6.x86_64.rpm
RUN wget http://puppetagain.pub.build.mozilla.org/data/repos/yum/releng/public/CentOS/6/noarch/mozilla-signing-test-files-1.2-1.noarch.rpm
RUN rpm -i --force *.rpm

WORKDIR /build
RUN hg clone https://hg.mozilla.org/build/tools
RUN /tools/python27/bin/python /tools/python27-virtualenv/bin/virtualenv venv
RUN venv/bin/pip install requests

RUN mkdir /builds/signing
RUN chown cltsign:cltsign /builds/signing
RUN chmod 0700 /builds/signing

CMD ["python2"]
