import os
import sys
import smtplib

from email import Encoders
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.Utils import formatdate

from M2Crypto import BIO, SMIME, X509
import smtplib, string, sys

def sendsmime(from_addr, to_addr, subject, msg, from_key, from_cert=None, smtpd='localhost'):
    
    msg_bio = BIO.MemoryBuffer(msg)
    sign = from_key
    
    s = SMIME.SMIME()
    s.load_key(from_key, from_cert)
    p7 = s.sign(msg_bio, flags=SMIME.PKCS7_TEXT)
    msg_bio = BIO.MemoryBuffer(msg) # Recreate coz sign() has consumed it.

    out = BIO.MemoryBuffer()
    out.write('From: %s\r\n' % from_addr)
    out.write('To: %s\r\n' % to_addr)
    out.write('Subject: %s\r\n' % subject)
    s.write(out, p7, msg_bio)

    out.close()
    smtp = smtplib.SMTP()
    smtp.connect(smtpd)
    smtp.sendmail(from_addr, to_addr, out.read())
    smtp.quit()

TO = "ivano.talamo@roma1.infn.it"
FROM="ivano.talamo@roma1.infn.it"
HOST = "141.108.26.220"

if len(sys.argv)!=2:
    print "error"
    sys.exit(1)

server=sys.argv[1]

filePath = r'/storage/local/security/certificates/%s/req.pem'%server
#filePath = r'/storage/local/management/scripts/cert-req/req.pem'

msg = MIMEMultipart()    
# attach a file
part = MIMEBase('application', "octet-stream")
part.set_payload( open(filePath,"rb").read() )
Encoders.encode_base64(part)
part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(filePath))
msg.attach(part)

print filePath
sendsmime("ivano.talamo@roma1.infn.it",
#          "talamoig@cern.ch",
#          "ivano.talamo@gmail.com",
#          "francesco.micheli@roma1.infn.it",
          "supporto@roma1.infn.it",
          "richiesta certificato server %s"%server,
          msg.as_string(),
          "/storage/local/security/certificates/globus/userkey.pem",
          "/storage/local/security/certificates/globus/usercert.pem",
          "141.108.26.222"
          )
