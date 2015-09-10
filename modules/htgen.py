#!/usr/bin/env python

# Code related to generating dynamic HTML content

# A note: HTML "id" attributes about message-specific elements
# are suffixed with "-{msgid" where {msgid} is the message id.

import os
from html import escape as html_escape
from html import unescape as html_unescape
import urllib
import email
import mimetypes

from modules import database

MAIN_TEMPLATE = """
<!doctype html>
<head>
    <title>tmail | {title}</title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <link rel="stylesheet" href="/static/style.css" />
    <script src="/static/script.js"></script> 
</head>
<body>
    <div class="topbar">
        <span class="logo">tmail</span>
        <form action="">
        <input type="search" name="search" class="search">
        </form>
        <a href="?refresh=true" class="refresh"><div>Refresh</div></a>
    </div>
    <div class="sidebar">
        <ol class="sidelinks">
            <li class="sidelink"><a id="sidelink-compose" href="/compose">Compose</a></li>
            <li class="divider"></li>
            <li class="sidelink"><a id="sidelink-inbox" href="/box/in">Inbox</a></li>
            <li class="sidelink"><a id="sidelink-outbox" href="/box/out">Outbox</a></li>
        </ol>
    </div>
    <div class="contentarea">
        {content}
    </div>
</body>
""" 

######################
# INBOXES / OUTBOXES #
######################

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
                            <table>
                            <tr><td style="color:#AAA;">F:</td><td>{sender}</td></tr>
                            <tr><td style="color:#AAA;">T:</td><td>{recip}</td></tr>
                            </table>
                        </div>
                        <div class ="info whatwhenbox">    
                            <div class="subject" style="font-weight: {weight};">{subj}</div>
                            <div class="date">{date}</div>
                        </div>
                        
                    </a>
                </li>""".format(msgid=msgid,sender=sender,recip=recip,weight=weight,subj=subj,date=date)
    msgs += "</ol>"
    return msgs





###################
# MESSAGE THREADS #
###################

THREADMESSAGE_404_TEMPLATE = """<li class="threadmessage" style="font-size:10px;"><i>The above message is in reply to another message, but that message could not be located.</i><br>{msgid}</li>"""

ATTACHMENT_DIRECTORY = "attachments/"
ATTACHMENT_TEMPLATE = """<span class="attachment"><a href={path}>{filename}</a></span>\n"""

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
                    <table class="infobox">
                        <tr class="info "id="subject-{msgid}">
                            <td class="prefix">Subj:</td>
                            <td class="value" style="font-weight:bold;">{subj}</td>
                        </tr>
                        <tr class="info "id="msgid-{msgid}" style="display:none;">
                            <td class="prefix">ID:</td>
                            <td class="value">{msgid}</td>
                        </tr>
                        <tr class="info "id="sender-{msgid}">
                            <td class="prefix">From:</td>
                            <td class="value">{sender}</td>
                        </tr>
                        <tr class="info "id="recipient-{msgid}">
                            <td class="prefix">To:</td>
                            <td class="value">{recip}</td>
                        </tr>
                        <tr class="info "id="date-{msgid}">
                            <td class="prefix">Date:</td>
                            <td class="value">{date}</td>
                        </tr>
                        <tr class="info "id="cc-{msgid}" style="display:none;">
                            <td class="prefix">CC:</td>
                            <td class="value">{cc}</td>
                        </tr>
                        <tr class="info "id="bcc-{msgid}" style="display:none;">
                            <td class="prefix">BCC:</td>
                            <td class="value">{bcc}</td>
                        </tr>
                    </table>
                    <div class="extended-toggle" onclick="toggleExtended('{msgid}');">Full details</div>
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




#################
#    COMPOSE    #
#################

INREPLYTO_HEADER_TEMPLATE = """<span class="reply-header">Replying to <a href="{inreplyto}">{inreplyto}</a></span>"""

def compose(wfile, recips=[], sender="", inreplyto=None, replyall=False):
    wfile.write(MAIN_TEMPLATE.format(title="Compose", content=get_compose_content(recips,sender,inreplyto, replyall)).encode("UTF-8"))
    
# The replyall recip list is constructed "using the contents
# of the original From, To and CC header as the default
# set of reply targets (with duplicates and possibly the
# replying user's address removed)."
# https://www.ietf.org/proceedings/43/I-D/draft-ietf-drums-replyto-meaning-00.txt

def get_compose_content(recips_normal, sender, inreplyto, replyall_enabled):
    html = ""
    # Add reply header
    if inreplyto:
        inreplyto_msg = email.message_from_string(database.get_message(inreplyto))
    if inreplyto_msg is not None:
        # Convert ["sam shelton <sam@shelt.ca>"] to ["sam@shelt.ca"] for to, cc, and from fields
        cc = [email.utils.parseaddr(field)[1] for field in inreplyto_msg.get("Cc").split(",")]
        to = [email.utils.parseaddr(field)[1] for field in inreplyto_msg.get("To").split(",")] #TODO remove self email from recips
        replyto = [email.utils.parseaddr(field)[1] for field in inreplyto_msg.get("Reply-To").split(",")]
        fr = email.utils.parseaddr(inreplyto_msg.get("From"))[1]
        # Merge lists
        recips_replyall = set(cc) | set(to) | set((fr,))
        recips_replyto = set(replyto)
        recip_sender = [fr] # No need to convert it to set; it's duplicate-free.

        html += INREPLYTO_HEADER_TEMPLATE.format(inreplyto=inreplyto)
        html += """
<script>
var recips_replyall = {recips_replyall};
var recips_replyto = {recips_replyto};
var recip_sender = {recip_sender};
</script>
""".format(recips_replyall=list(recips_replyall), recips_replyto=list(recips_replyto), recip_sender=recip_sender)

        html += """
            <fieldset id="replymode-fieldset" class="replymode">
                <div>
                    <label class="selected">
                      Reply-to
                      <input name="replymode" onclick="radioChange(this);setToList(recips_replyto);" type="radio" value="reply_to" checked />
                    </label>
                    <label>
                      Sender
                      <input name="replymode" onclick="radioChange(this);setToList(recip_sender);" type="radio" value="sender" />
                    </label>
                    <label class="warning">
                      Reply-All
                      <input name="replymode" onclick="radioChange(this);setToList(recips_replyall);" type="radio" value="reply_all" />
                    </label>
                </div>
            </fieldset>
        """
    # note the end of above if block
    html += """
    <ol id="recips" class="recips">
    </ol>
    <input type="text" name="addrecip" class="addrecip" onkeypress="addRecip(this);">
    {from_account}
    """.format(from_account=get_accounts_dropdown())
    return html

ACCOUNTS_DROPDOWN_TEMPLATE = """<option {selected} value="{address}">{name} &lt;{address}&gt;</option>\n"""
def get_accounts_dropdown(sender=""):
    default_sender = "sam@shelt.ca" #database.get_setting("default_sender") #TODO SETTINGS SHOULD BE RETRIEVED ONE TIME AND STORED IN GLOBALS

    text = """<select class="sender">\n"""
    for account in database.get_account_list():
        if sender == "":
            if account[0] == default_sender:
                selected = "selected"
            else:
                selected = ""
        else:
            selected = sender
        text += ACCOUNTS_DROPDOWN_TEMPLATE.format(selected=selected, address=account[0], name=account[1])
    text += "</select>\n"
    return text


#################
# MISCELLANEOUS #
#################

# Fix html module functions to handle None inputs
def escape(string):
    if string is None:
        return "None"
    return html_escape(string)
def unescape(string):
    if string is None:
        return "None"
    return html_unescape(string)
