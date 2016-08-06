KEYSTORE=jar
KEYNAME=jar
KEYPASS=jarpass
echo "Use $KEYPASS for the password. 6 returns and a 'yes', then return"
keytool -keystore $KEYSTORE -genkey -alias $KEYNAME -keysize 2048 -keyalg RSA -validity 10000

echo "Now copy 'jar' into docker/"
