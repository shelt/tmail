#!/usr/bin/env python

# This module uses IMAP4 to retrieve raw message data
# from mailservers. It will import such data into the
# sqlite database.

from getpass import getpass
import imaplib

from modules import database


# This function retrieves the newest mail of an address from the mailserver
# and imports it into the database.
def retrieve(address):
    accid,username,host,port = database.get_incoming_credentials(address)
    m = imaplib.IMAP4_SSL(host,port)
    m.login(username, getpass())
    m.select()
    (typ, data) = m.search(None, 'ALL')
    for num in data[0].split():
        # Get raw data
        typ, data_part = m.fetch(num, '(RFC822)')
        data = data_part[0][1]
        
        # Insert into mail db
        database.add_raw_message(accid, data)
    m.close()
    m.logout()
