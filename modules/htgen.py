#!/usr/bin/env python

# Code that generates html dynamically.
from html import escape
import urllib
import email

from modules import database

TEMPLATE = """
<!doctype html>
<head>
    <title>ｔ {title}</title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <link rel="stylesheet" href="/static/style.css" />
    <script src="/static/script.js"></script> 
</head>
<body>
    <div class="topbar">
        <span class="logo">tmail</span>
    </div>
    <div class="sidebar">
        <ol class="sidelinks">
            <li class="sidelink"><a id="sidelink-refresh" href="/compose">Compose</a></li>
            <li class="divider"></li>
            <li class="sidelink"><a id="sidelink-inbox" href="http://localhost:8000/box/in">Inbox</a></li>
            <li class="sidelink"><a id="sidelink-outbox" href="http://localhost:8000/box/out">Outbox</a></li>
        </ol>
    </div>
    <div class="contentarea">
        {content}
    </div>
</body>
""" 

def box(wfile, boxtype):
    wfile.write(TEMPLATE.format(title=boxtype+"box", content=get_box_content(boxtype)).encode("UTF-8"))

def get_box_content(boxtype):
    if boxtype == "in":
        raw_msgs = database.get_inbox()
    elif boxtype == "out":
        raw_msgs = database.get_outbox()
    else:
        raise ValueError("Unknown boxtype: "+boxtype)

    # Sorting by date   
    DATE_INDEX = 1 
    try:
        import operator
    except ImportError:
        sortkey = key=operator.itemgetter(DATE_INDEX)
    else:
        sortkey = lambda x: x[DATE_INDEX]
    raw_msgs.sort(key=sortkey, reverse=True)

    # Adding messages
    msgs = """<ol class="messages">
"""
    for raw_msg in raw_msgs:
        if raw_msg[2] == 1: # is read?
            weight = "bold"
        else:
            weight = "normal"
        msg = email.message_from_string(raw_msg[0])
        msgid  = escape(msg.get("Message-ID"))
        sender = escape(msg.get("From"))
        recip  = escape(msg.get("To"))
        subj   = escape(msg.get("Subject"))
        date   = escape(msg.get("Date"))

        msgs += """
                <li class="message">
                    <a href="/thread/{msgid}">
                        <div class="info whobox">
                            <div class="sender">{sender}</div>
                            <div class="recipient">{recip}</div>
                        </div>
                        <div class ="info whatwhenbox">    
                            <div class="subject" style="font-weight: {weight};">{subj}</div>
                            <div class="date">{date}</div>
                        </div>
                        
                    </a>
                </li>""".format(msgid=msgid,sender=sender,recip=recip,weight=weight,subj=subj,date=date)
    msgs += "</ol>"
    return msgs








def thread(wfile, rootid):
    wfile.write(TEMPLATE.format(title="thread", content=get_thread_content(rootid)).encode("UTF-8"))


def get_thread_content(rootid):
    msgs = """<lo class="threadmessages">
"""
    currid = rootid
    while True:
        result = get_thread_message(currid)
        msgs += result[0]
        currid = result[1]
        if currid == None or currid == "None":
            break
    msgs += "</ol>"
    return msgs

# Called recursively get_thread_content
def get_thread_message(msgid):
    msg = email.message_from_string(database.get_message(msgid, mark_read=True))
    if not msg:
        return ('<li class="threadmessage">[Message not found]<br>'+msgid+'</li>',None)
    subj      = escape(str(msg.get("Subject")))
    msgid     = escape(str(msg.get("Message-ID")))
    sender    = escape(str(msg.get("From")))
    recip     = escape(str(msg.get("To")))
    date      = escape(str(msg.get("Date")))
    cc        = escape(str(msg.get("Cc")))
    bcc       = escape(str(msg.get("Bcc")))
    inreplyto = escape(str(msg.get("In-Reply-To")))
    body      = escape(str(get_message_body(msg)))

    msg_html = """
            <li class="threadmessage">
                <div class="subject">{subj}</div>
                <div class="infobox">
                    <div class="msgid">{msgid}</div>
                    <div class="sender">{sender}</div>
                    <div class="recipient">{recip}</div>
                    <div class="date">{date}</div>
                    <div class="cc">{cc}</div>
                    <div class="bcc">{bcc}</div>
                    <div class="inreplyto">{inreplyto}</div>
                    <div class="extended-toggle" onclick="toggleExtended">...</div>
                </div>
                <div class="body">{body}</div>
            </li>""".format(subj=subj, msgid=msgid, sender=sender, recip=recip, date=date, cc=cc, bcc=bcc, inreplyto=inreplyto, body=body)
    return (msg_html,inreplyto)

def get_message_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                return part.get_payload()
    elif msg.get_content_type() == 'text/plain':
        return msg.get_payload()
    else:
        return "Message is HTML. TODO: implement HTML-To-Plain parsing."
