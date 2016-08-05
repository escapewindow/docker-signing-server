cd /builds/signing/signing1
echo "passwords:
    gpg:
    authenticode: qwerqwer
"
bin/python tools/release/signing/signing-server.py -l signing.log -d signing.ini
