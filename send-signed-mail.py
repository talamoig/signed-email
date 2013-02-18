import os
import sys
import smtplib
import dns.resolver

from optparse import OptionParser
from M2Crypto import BIO, SMIME, X509
from os.path import expanduser
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
    try:
        smtp.connect(smtpd)
        smtp.sendmail(from_addr, to_addr, out.read())
        smtp.quit()
        return 0
    except Exception:        
        return 1

def usageError(msg,exitcode=1):
    print(msg)
    parser.print_help()
    sys.exit(exitcode)

def main():
    parser.add_option("-g", "--globusdir", dest="globusdir", metavar="FILE", default="%s/%s"%(expanduser("~"),".globus"),
                      help="directory containing usercert.pem and userkey.pem (default ~/.globus/)")
    parser.add_option("-a", "--attach", dest="attachfile", metavar="FILE", 
                      help="file to be attached to the email")
#    parser.add_option("-b", "--body", dest="bodyfile", metavar="FILE", 
#                      help="file containing the mail body [not impemented yet]")
    parser.add_option("-s", "--subject", dest="subject", 
                      help="email subject")
    parser.add_option("-f", "--from", dest="mailfrom", 
                      help="from field")
    parser.add_option("-m", "--mailserver", dest="smtpd", default=None,
                      help="SMTP server address")
    
    (options, args) = parser.parse_args()
    if len(args) != 1:
        usageError("Please specify a destination mail address")
    if options.attachfile==None:
        usageError("Please specify an attachment")

    tocheck=[options.attachfile,"%s/usercert.pem"%options.globusdir,"%s/userkey.pem"%options.globusdir]
    for file in tocheck:
        if os.path.isfile(file):
            try:
                open(file)
            except IOError:
                usageError('Cannot open file %s'%file)
        else:
            usageError("File %s does not exists."%file)
           
    msg = MIMEMultipart()
##    if options.bodyfile!=None:
##        msg.preamble = open(options.bodyfile, 'r').read()
    ## attachment
    part = MIMEBase('application', "octet-stream")
    part.set_payload( open(options.attachfile,"rb").read() )
    Encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(options.attachfile))
    msg.attach(part)
    recipient=args[0]
    if options.smtpd!=None:
        smtpdlist=[options.smtpd]
    else:
        parts=options.mailfrom.split("@")
        if len(parts)!=2:
            usageError("Malformed recipient")
        domain=parts[1]
        answers = dns.resolver.query(domain, 'MX')
        smtpdlist=[]
        for rdata in answers:
            smtpdlist.append("%s"%rdata.exchange)
    print smtpdlist
    if len(smtpdlist)==0:
        print("No smtpd server found for domain %s"%domain)
        sys.exit(1)
    for smtpd in smtpdlist:
        ret=sendsmime(options.mailfrom,
                      recipient,
                      options.subject,
                      msg.as_string(),
                      options.globusdir+"/userkey.pem",
                      options.globusdir+"/usercert.pem",
                      smtpd)
        if ret==0: break
    sys.exit(ret)

usage = "usage: %prog [options] sitename"
parser = OptionParser(usage)
if __name__ == "__main__":
        main()
                                        
