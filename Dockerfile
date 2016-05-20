FROM centos:centos6

RUN yum -y update \
        && yum -y install curl gcc gnupg openssl libevent libevent-devel java-1.6.0-openjdk-devel mono-core mono-devel nss-tools wget mercurial tcl-devel tk-devel

RUN mkdir /code
WORKDIR /code
RUN wget http://puppetagain.pub.build.mozilla.org/data/repos/yum/releng/public/CentOS/6/x86_64/signmar-19.0-2.el6.x86_64.rpm
RUN wget http://puppetagain.pub.build.mozilla.org/data/repos/yum/custom/osslsigncode/x86_64/osslsigncode-1.7.1-1.el6.x86_64.rpm
RUN wget http://puppetagain.pub.build.mozilla.org/data/repos/yum/releng/public/CentOS/6/x86_64/mozilla-python27-2.7.3-1.el6.x86_64.rpm
RUN wget http://puppetagain.pub.build.mozilla.org/data/repos/yum/releng/public/CentOS/6/x86_64/mozilla-python27-virtualenv-1.7.1.2-2.el6.x86_64.rpm
RUN wget http://puppetagain.pub.build.mozilla.org/data/repos/yum/releng/public/CentOS/6/noarch/mozilla-signing-test-files-1.2-1.noarch.rpm
RUN rpm -i --force *.rpm

WORKDIR /code
RUN hg clone https://hg.mozilla.org/build/tools
RUN /tools/python27/bin/python /tools/python27-virtualenv/bin/virtualenv venv
RUN venv/bin/pip install requests

CMD ["python2"]
