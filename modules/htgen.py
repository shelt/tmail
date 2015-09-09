#!/usr/bin/env python

# Code related to generating dynamic HTML content

import os
from html import escape as html_escape
from html import unescape as html_unescape
import urllib
import email
import mimetypes

from modules import database

ATTACHMENT_DIRECTORY = "attachments/"
ATTACHMENT_TEMPLATE = """<span class="attachment"><a href={path}>{filename}</a></span>\n"""

THREADMESSAGE_404_TEMPLATE = """<li class="threadmessage" style="font-size:10px;"><i>The above message is in reply to another message, but that message could not be located.</i><br>{msgid}</li>"""

MAIN_TEMPLATE = """
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
    wfile.write(MAIN_TEMPLATE.format(title=boxtype+"box", content=get_box_content(boxtype)).encode("UTF-8"))

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
    msgs = """<ol class="boxmessages">
"""
    for raw_msg in raw_msgs:
        if raw_msg[2] == 1: # is read?
            weight = "normal"
        else:
            weight = "bold"
        msg = email.message_from_string(raw_msg[0])
        msgid  = escape(msg.get("Message-ID"))
        sender = escape(msg.get("From"))
        recip  = escape(msg.get("To"))
        subj   = escape(msg.get("Subject"))
        date   = escape(msg.get("Date"))

        msgs += """
                <li class="boxmessage">
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
    wfile.write(MAIN_TEMPLATE.format(title="thread", content=get_thread_content(rootid)).encode("UTF-8"))


def get_thread_content(rootid):
    msgs = """<ol class="threadmessages">\n"""
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
        return (THREADMESSAGE_404_TEMPLATE.format(msgid=escape(msgid)),None)
    subj      = escape(msg.get("Subject"))
    msgid     = escape(msg.get("Message-ID"))
    sender    = escape(msg.get("From"))
    recip     = escape(msg.get("To")).replace(",","<br>")
    date      = escape(msg.get("Date"))
    cc        = escape(msg.get("Cc")).replace(",","<br>")
    bcc       = escape(msg.get("Bcc")).replace(",","<br>")
    inreplyto = escape(msg.get("In-Reply-To"))

    (body,attachments) = get_message_body(msg)
    
    body = escape(body)
    # Hide quoted text
    # Text should be quoted if it starts with a "> ", or
    # if the line above or below it does (because some mail
    # clients are bad at word wrapping)
    lines = body.splitlines()
    i = 0
    already_quoting = False
    last_quoted_line = None
    for i in range(len(lines)):
        if lines[i].startswith("&gt; "):
            last_quoted_line = i
            if not already_quoting:
                lines[i] = '\n<input type="checkbox" class="showquote"><div class="quote">\n' + lines[i]
                already_quoting = True
            elif (i - last_quoted_line) > 1:
                lines[i] = lines[i] + '\n</div"><\n'
                already_quoting = False
    body = "\n".join(lines)
        
    


    msg_html = """
            <li class="threadmessage">
                <div class="threadmessage">
                    <div class="threadbutton">todo</div>
                    <table class="infobox">
                        <tr class="info "id="subject">
                            <td class="prefix">Subj:</td>
                            <td class="value" style="font-weight:bold;">{subj}</td>
                        </tr>
                        <tr class="info "id="msgid">
                            <td class="prefix">ID:</td>
                            <td class="value">{msgid}</td>
                        </tr>
                        <tr class="info "id="sender">
                            <td class="prefix">From:</td>
                            <td class="value">{sender}</td>
                        </tr>
                        <tr class="info "id="recipient">
                            <td class="prefix">To:</td>
                            <td class="value">{recip}</td>
                        </tr>
                        <tr class="info "id="date">
                            <td class="prefix">Date:</td>
                            <td class="value">{date}</td>
                        </tr>
                        <tr class="info "id="cc">
                            <td class="prefix">CC:</td>
                            <td class="value">{cc}</td>
                        </tr>
                        <tr class="info "id="bcc">
                            <td class="prefix">BCC:</td>
                            <td class="value">{bcc}</td>
                        </tr>
                    </table>
                    <div class="extended-toggle" onclick="toggleExtended">...</div>
                    <div class="body">{body}</div>
                    <div class="attachments">{attachments}</div>
                </div>
            </li>""".format(subj=subj, msgid=msgid, sender=sender, recip=recip,date=date, 
                            cc=cc, bcc=bcc, inreplyto=inreplyto, body=body, attachments=attachments)
    return (msg_html,unescape(inreplyto))

def get_message_body(msg):
    plain       = ""
    attachments = ""
    if msg.is_multipart():
        counter = 1
        for part in msg.walk():
            ctype = part.get_content_type()
            cdisp = part.get("Content-Disposition")
            if cdisp is not None and\
            (cdisp.lower().startswith("attachment") or cdisp.lower().startswith("inline")):
                # Set most appropriate filename
                filename = part.get_filename()
                if not filename:
                    ext = mimetypes.guess_extension(part.get_content_type())
                    if not ext:
                        # Generic extension
                        ext = '.bin'
                    filename = 'untitled-%03d%s' % (counter, ext)

                # Save attachment
                counter += 1
                with open(os.path.join(ATTACHMENT_DIRECTORY, filename), 'wb') as fp:
                    fp.write(part.get_payload(decode=True))

                # Add link to body
                attachments += ATTACHMENT_TEMPLATE.format(path="/" + ATTACHMENT_DIRECTORY+filename,filename=filename)
            elif ctype == 'text/plain':
                plain += part.get_payload()
    elif msg.get_content_type() == 'text/plain':
        plain = msg.get_payload()
    else:
        plain = "Message has no text/plain part. TODO: implement HTML-To-Plain parsing."
    return (plain,attachments)


# Fix html module functions to handle None inputs
def escape(string):
    if string is None:
        return "None"
    return html_escape(string)
def unescape(string):
    if string is None:
        return "None"
    return html_unescape(string)
