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
from jinja2 import Environment
from jinja2.loaders import FileSystemLoader

from modules import database

TEMPLATE_DIR = "templates"
# Load templates
loader = FileSystemLoader(TEMPLATE_DIR)
env = Environment(line_statement_prefix='%',
      variable_start_string="{{",
      variable_end_string="}}",
      loader=loader)

temp_base = env.get_template("base.html")
temp_box = env.get_template("box.html", parent=temp_base)
temp_thread = env.get_template("thread.html", parent=temp_base)
temp_compose = env.get_template("compose.html", parent=temp_base)



######################
# INBOXES / OUTBOXES #
######################

def box(wfile,boxtype):
    msgs = []
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

    for raw_msg in raw_msgs:
        msg = {}
        msg['read'] = raw_msg[2] == 1
        
        parsed = email.message_from_string(raw_msg[0])
        msg['msgid']  = escape(parsed.get("Message-ID"))
        msg['sender'] = escape(parsed.get("From"))
        msg['recip']  = escape(parsed.get("To"))
        msg['subj']   = escape(parsed.get("Subject"))
        msg['date']   = escape(parsed.get("Date"))
        
        msgs.append(msg)
    
    html = temp_box.render(boxtype=boxtype, msgs=msgs)
    wfile.write(html.encode("UTF-8"))

###################
# MESSAGE THREADS #
###################

ATTACHMENT_DIRECTORY = "attachments/" # TODO move

#def thread(wfile, rootid):
#    wfile.write(MAIN_TEMPLATE.format(title="thread", content=get_thread_content(rootid)).encode("UTF-8"))


def thread(wfile,rootid):
    msgs = []
    nextid = rootid
    while True:
        msg = get_thread_message(nextid)
        msgs.append(msg)
        if msg is None or msg['inreplyto'] == None:
            break
        nextid = unescape(msg['inreplyto'])
    html = temp_thread.render(msgs=msgs)
    wfile.write(html.encode("UTF-8"))

def get_thread_message(msgid):
    result = database.get_message(msgid, mark_read=True)
    if result is None:
        return None
    parsed = email.message_from_string(result)
    msg = {}
    msg['subj']      = escape(parsed.get("Subject"))
    msg['msgid']     = escape(parsed.get("Message-ID"))
    msg['sender']    = escape(parsed.get("From"))
    msg['recip']     = escape(parsed.get("To"))
    msg['date']      = escape(parsed.get("Date"))
    msg['cc']        = escape(parsed.get("Cc"))
    msg['bcc']       = escape(parsed.get("Bcc"))
    msg['inreplyto'] = escape(parsed.get("In-Reply-To"))
    
    if msg['recip'] is not None: msg['recip'] = msg['recip'].replace(",","<br>")
    if msg['cc'] is not None: msg['cc'] = msg['cc'].replace(",","<br>")
    if msg['bcc'] is not None: msg['bcc'] = msg['bcc'].replace(",","<br>")

    (body,attachments) = get_message_body(parsed)
    body = escape(body)
    msg['attachments'] = attachments
    
    # Hide quoted text #
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
        
    msg['body'] = body
    
    return msg

def get_message_body(msg):
    plain       = ""
    attachments = []
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
                attachments.append({"path":"/" + ATTACHMENT_DIRECTORY+filename, "filename":filename})
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

def compose(wfile, inreplyto=None, replyall=False):
    wfile.write(MAIN_TEMPLATE.format(title="Compose", content=get_compose_content(None,inreplyto, replyall)).encode("UTF-8"))
    
# The replyall recip list is constructed "using the contents
# of the original From, To and CC header as the default
# set of reply targets (with duplicates and possibly the
# replying user's address removed)."
# https://www.ietf.org/proceedings/43/I-D/draft-ietf-drums-replyto-meaning-00.txt

def get_compose_content(sender, inreplyto, replyall_enabled): # note sender is unused; see todo
    html = ""
    # Add reply header
    inreplyto_msg = None
    if inreplyto:
        inreplyto_msg = email.message_from_string(database.get_message(inreplyto))
    if inreplyto_msg is not None:
        # Convert ["sam shelton <sam@shelt.ca>"] to ["sam@shelt.ca"] for to, cc, and from fields
        cc = [email.utils.parseaddr(field)[1] for field in inreplyto_msg.get("Cc").split(",")]
        to = [email.utils.parseaddr(field)[1] for field in inreplyto_msg.get("To").split(",")] #TODO remove self email from recips
        replyto = [email.utils.parseaddr(field)[1] for field in inreplyto_msg.get("Reply-To").split(",")]
        fr = email.utils.parseaddr(inreplyto_msg.get("From"))[1]
        # Merge lists for use in script element
        recips_replyall = set(cc) | set(to) | set((fr,))
        recips_replyto = set(replyto)
        recip_sender = [fr] # No need to convert it to set; it's duplicate-free.

        html += INREPLYTO_HEADER_TEMPLATE.format(inreplyto=inreplyto)
        html += """
            <fieldset id="replymode-fieldset" class="replymode">
                <div>
                    <label class="selected">
                      Reply-to
                      <input name="replymode" onclick="radioChange(this);setToList(recips_replyto);" type="radio" value="reply_to" />
                    </label>
                    <label>
                      Sender
                      <input name="replymode" onclick="radioChange(this);setToList(recip_sender);" type="radio" value="sender" />
                    </label>
                    <label>
                      Reply-All
                      <input name="replymode" onclick="radioChange(this);setToList(recips_replyall);" type="radio" value="reply_all" />
                    </label>
                </div>
            </fieldset>
            <script>
                var recips_replyall = {recips_replyall};
                var recips_replyto = {recips_replyto};
                var recip_sender = {recip_sender};
                if ({replyall_enabled})
            </script>
        """.format(recips_replyall=list(recips_replyall), recips_replyto=list(recips_replyto), recip_sender=recip_sender)
    # note the end of above if inreplyto block
    html += """
    <ol id="recips" class="recips">
    </ol>
    <input type="text" name="addrecip" class="addrecip" onkeypress="addRecip(this);">
    {from_account}
    <script>
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
        return None
    return html_escape(string)
def unescape(string):
    if string is None:
        return None
    return html_unescape(string)
