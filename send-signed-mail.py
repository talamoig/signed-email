import os
import sys
import smtplib

from optparse import OptionParser
from M2Crypto import BIO, SMIME, X509
import smtplib, string, sys

from email import Encoders
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.Utils import formatdate

def sendsmime(from_addr, to_addr, subject, msg, from_key, from_cert, smtpd):
    
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

def main():
    usage = "usage: %prog [options] sitename"
    parser = OptionParser(usage)
    parser.add_option("-g", "--globusdir", dest="globusdir", metavar="FILE",
                      help="directory containing usercert.pem and userkey.pem (default ~/.globus/)")
    parser.add_option("-a", "--attach", dest="attachfile", metavar="FILE", 
                      help="file to be attached to the email")
    parser.add_option("-b", "--body", dest="bodyfile", metavar="FILE", 
                      help="file containing the mail body")
    parser.add_option("-s", "--subject", dest="subject", 
                      help="email subject")
    parser.add_option("-f", "--from", dest="mailfrom", 
                      help="from field")
    parser.add_option("-m", "--mailserver", dest="smtpd", 
                      help="SMTP server address")
    
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("Please specify a destination mail address")
        sys.exit(1)
    msg = MIMEMultipart()
##    if options.bodyfile!=None:
##        msg.preamble = open(options.bodyfile, 'r').read()
    ## attach a file
    part = MIMEBase('application', "octet-stream")
    part.set_payload( open(options.attachfile,"rb").read() )
    Encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(options.attachfile))
    msg.attach(part)

    print msg.as_string()
    sendsmime(options.mailfrom,
              args[0],
              options.subject,
              msg.as_string(),
              options.globusdir+"/userkey.pem",
              options.globusdir+"/usercert.pem",
              options.smtpd
              )
        
if __name__ == "__main__":
        main()
                                        
