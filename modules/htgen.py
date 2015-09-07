#!/usr/bin/env python

# Code that generates html dynamically.
from html import escape
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
    </div>
    <div class="sidebar">
        <ol class="sidelinks">
            <li class="sidelink"><a id="sidelink-inbox" href="http://localhost:8000/box/in">Inbox</a></li>
            <li class="sidelink"><a id="sidelink-outbox" href="http://localhost:8000/box/out">Outbox</a></li>

            <form id="refresh" method="post" action="#">
            <li class="sidelink" id="refresh"><button type="submit" form="refresh" value="refresh">Refresh</button></li>
        </ol>
    </div>
    <div class="contentarea">
        <ol class="messages">
            {messages}
        </ol>
    </div>
</body>
""".format(title=boxtype, messages=get_messages_list(boxtype)).encode("UTF-8"))

def get_messages_list(boxtype):
    if boxtype == "in":
        raw_msgs = database.get_inbox()
    elif boxtype == "out":
        raw_msgs = database.get_outbox()
    else:
        raise ValueError("Unknown boxtype: "+boxtype)
    body = ""
    for raw_msg in raw_msgs:
        body = raw_msg[0]
        if raw_msg[1] == 1: # is read?
            weight = "bold"
        else:
            weight = "normal"
        msg = email.message_from_string(body.decode())
        msgid  = escape(msg.get("Message-ID"))
        sender = escape(msg.get("From"))
        recip  = escape(msg.get("To"))
        subj   = escape(msg.get("Subject"))
        date   = escape(msg.get("Date"))

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
