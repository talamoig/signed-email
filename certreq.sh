#!/bin/bash
if [ $# -ne 1 ]
    then
    echo "Please specify the fqdn of the server."
    exit 1
fi
FQDN=$1
SUBJECT="richiesta certificato server $FQDN"
TO=supporto@roma1.infn.it
FROM=ivano.talamo@roma1.infn.it
echo -e "Roma 1\n$FQDN\n$FROM" |openssl req -new -nodes -out req.pem -keyout hostkey.pem -config host.conf
echo -e "\n"
chmod 444 hostkey.pem
mkdir -p $FQDN
mkdir -p $FQDN-new
mv hostkey.pem req.pem $FQDN-new
rm -f mail-body mail-body.signed
mpack -s "$SUBJECT" -o mail-body cmsrm-st13.roma1.infn.it-new/req.pem
openssl smime -sign -in mail-body -signer /cmshome/talamoig/.globus/usercert.pem -from $FROM -to $TO -inkey /cmshome/talamoig/.globus/userkey.pem -subject "$SUBJECT" | sendmail $TO
