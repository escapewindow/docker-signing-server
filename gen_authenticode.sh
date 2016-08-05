#!/bin/sh -ex
PASS="qwerqwer"
SUBJ="/C=US/ST=confusion/L=Springfield/O=Bikeshed/CN=Mozilla Fake CA"
tmpdir=authenticode.tmp

rm -rf "$tmpdir"
mkdir -p "$tmpdir"
pushd "$tmpdir"

openssl req -x509 -days 7200 -sha256 -newkey rsa:4096 -subj "$SUBJ" -keyout MozFakeCA.key -out MozFakeCA.pem -outform PEM -passin pass:$PASS -passout pass:$PASS
openssl genrsa -passout pass:$PASS  -out MozAuthenticode.key -des3 4096
openssl req -new -key MozAuthenticode.key -passin pass:$PASS -subj "$SUBJ" -out MozAuthenticode.csr
openssl x509 -req -sha256 -days 7200 -in MozAuthenticode.csr -CA MozFakeCA.pem -CAcreateserial -CAkey MozFakeCA.key -passin pass:$PASS -out MozAuthenticode.pem -outform PEM
openssl rsa -passin pass:$PASS -passout pass:$PASS -in MozAuthenticode.key -outform PVK -pvk-strong -out MozAuthenticode.pvk
openssl crl2pkcs7 -nocrl -certfile MozAuthenticode.pem -outform DER -out MozAuthenticode.spc

popd
echo "Done.  Now you can copy $tmpdir/MozAuthenticode.spc and $tmpdir/MozAuthenticode.pvk into docker/authenticode/"
