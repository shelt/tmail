#!/usr/bin/env python

# Code that generates html dynamically.
import email

from modules import database


def box(wfile, boxtype):
    wfile.write("""
<!doctype html>
<head>
    <title>ｔ {title}</title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <link rel="stylesheet" href="style.css" />
    <script src="script.js"></script> 
</head>
<body>
    <div class="topbar">
        <span class="logo">tmail</span>
        <a class="refresh">Refresh</a>
    </div>
    <div class="sidebar">
        <ol class="sidelinks">
            <li class="sidelink"><a href="/box/in">Inbox</a></li>
            <li class="sidelink"><a href="/box/out">Outbox</a></li>
        </ol>
    </div>
    <div class="contentarea">
        <ol class="messages">
            {messages}
        </ol>
    </div>
</body>
""".format(title=boxtype, messages=get_messages_list(boxtype)).encode())

def get_messages_list(boxtype):
    if boxtype == "in":
        raw_msgs = database.get_inbox()
    elif boxtype == "out":
        raw_msgs = database.get_outbox()
    body = ""
    for raw_msg in raw_msgs:
        body = raw_msg[0]
        if raw_msg[1] == 1: # is read?
            weight = "bold"
        else:
            weight = "normal"
        msg = email.message_from_string(body.decode())
        msgid = msg.get("Message-ID")
        sender = msg.get("From")
        recip  = msg.get("To")
        subj   = msg.get("Subject")
        date   = msg.get("Date")

    string = """
            <li class="message">
                <a href="/thread/{msgid}">
                    <div class="info sender">{sender}</div>
                    <div class="info recipient">{recip}</div>
                    <div class="info subject" style="font-weight: {weight};">{subj}</div>
                    <div class="info date">{date}</div>
                </a>
            </li>""".format(msgid=msgid,sender=sender,recip=recip,weight=weight,subj=subj,date=date)
    return string
