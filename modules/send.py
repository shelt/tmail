#!/usr/bin/env python

#
#
from getpass import getpass
import smtplib
import mimetypes
from email import utils
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
from datetime import datetime

import database


def send_message(from_address, to_address, message):
    # Sanity check
    if "Message-ID" not in message:
        raise ValueError("Messages is malformed or improperly generated.")
        return
    (accid,username,host,port) = database.get_outgoing_credentials(from_address)
    m = smtplib.SMTP_SSL(host,port)
    m.login(username, getpass())
    m.sendmail(from_address, to_address, message)
    m.quit()


def generate_message(from_name, from_address, to_address, subject, text, cc=[], bcc=[], in_reply_to=None, attachments=[]): 
    if attachments:
        msg = MIMEMultipart()
    else:
        msg = MIMEText(text, 'plain')
    msg.add_header("Message-ID",gen_message_id(from_address))
    msg.add_header("Return-Path",angle_enclose(from_address))
    msg.add_header("Date",utils.formatdate())
    msg.add_header("From", from_name +" "+ angle_enclose(from_address))
    msg.add_header("To",to_address)
    msg.add_header("Subject",subject)
    if in_reply_to is not None:
        msg.add_header("In-Reply-To",angle_enclose(in_reply_to))
    
    for attachment in attachments:
        msg.attach(generate_attachment(attachment))
    
    return msg.as_string()
    


def angle_enclose(string):
    return "<" + string.strip(" <>") + ">"

def gen_message_id(address):
    msgid = ""
    msgid += datetime.now().strftime("%Y%m%d%H%M%S")
    msgid += str(random.getrandbits(128))
    msgid = base36encode(int(msgid))
    msgid += "@" + address.split("@")[1]
    return angle_enclose(msgid)



def base36encode(number):
    if not isinstance(number, (int, long)):
        raise TypeError('number must be an integer')
    if number < 0:
        raise ValueError('number must be positive')
    
    alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    
    base36 = ''
    while number:
        number, i = divmod(number, 36)
        base36 = alphabet[i] + base36
    
    return base36 or alphabet[0]


def generate_attachment(path):
    if not os.path.isfile(path):
        raise IOError("File does not exist")
    # Guess the content type based on the file's extension.  Encoding
    # will be ignored, although we should check for simple things like
    # gzip'd or compressed files.
    ctype, encoding = mimetypes.guess_type(path)
    if ctype is None or encoding is not None:
        # No guess could be made, or the file is encoded (compressed), so
        # use a generic bag-of-bits type.
        ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)
    if maintype == 'text':
        fp = open(path)
        # Note: we should handle calculating the charset
        attachment = MIMEText(fp.read(), _subtype=subtype)
        fp.close()
    elif maintype == 'image':
        fp = open(path, 'rb')
        attachment = MIMEImage(fp.read(), _subtype=subtype)
        fp.close()
    elif maintype == 'audio':
        fp = open(path, 'rb')
        attachment = MIMEAudio(fp.read(), _subtype=subtype)
        fp.close()
    else:
        fp = open(path, 'rb')
        attachment = MIMEBase(maintype, subtype)
        attachment.set_payload(fp.read())
        fp.close()
        # Encode the payload using Base64
        encoders.encode_base64(attachment)
    # Set the filename parameter
    attachment.add_header('Content-Disposition', 'attachment', filename=filename)
    return attachment
