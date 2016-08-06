cd /builds/signing/signing1
echo "USE THESE PASSWORDS (blank line is no password):
    gpg passphrase:
    jar passphrase: jarpass
"
bin/python tools/release/signing/signing-server.py -v -l signing.log -d signing.ini
