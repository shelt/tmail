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
""".format(title=boxtype+"box", logo="tmail."+boxtype+"box", content=get_message_content(boxtype)).encode("UTF-8"))

def get_message_content(boxtype):
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
        body = raw_msg[0]
        if raw_msg[2] == 1: # is read?
            weight = "bold"
        else:
            weight = "normal"
        msg = email.message_from_string(body)
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













def thread(wfile, threadid):
    
