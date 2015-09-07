#!/usr/bin/env python

# Code related to serving hypertext.

import sys,os
import re
from urllib import parse
from mimetypes import guess_type
from http.server import HTTPServer, BaseHTTPRequestHandler
from http.cookies import SimpleCookie

from modules import htgen

# Content-Types associated with extensions
CTYPE_PATH = {
".html"    :"text/html",
".css"     :"text/css",
".css.map" :"text/css",
".jpg"     :"image/jpg",
".jpeg"    :"image/jpg",
".png"     :"image/png",
".ico"     :"image/ico",
".js"      :"text/javascript",
".json"    :"application/json",
".eot"     :"application/vnd.ms-fontobject",
".otf"     :"application/font-sfnt",
".svg"     :"image/svg+xmlt",
".ttf"     :"application/font-sfnt",
".woff"    :"application/font-woff"
}

# Whether or not file extensions belong to binary files
CTYPE_ISBINARY = {
".html"    :False,
".css"     :False,
".css.map" :False,
".jpg"     :True,
".jpeg"    :True,
".png"     :True,
".ico"     :True,
".js"      :False,
".json"    :False,
".eot"     :False,
".otf"     :False,
".svg"     :False,
".ttf"     :True,
".woff"    :True
}

CTYPE_ISCACHE = {
".html"    :False,
".css"     :True,
".css.map" :True,
".jpg"     :False,
".jpeg"    :False,
".png"     :False,
".ico"     :False,
".js"      :True,
".json"    :True,
".eot"     :True,
".otf"     :True,
".svg"     :True,
".ttf"     :True,
".woff"    :True
}


class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers['Content-Length'])
        post_data = parse.parse_qs(self.rfile.read(length).decode('utf-8'))
        print(post_data) #todo
    
        
    def do_GET(self):
        print(self.path)
        self.path = self.path.rstrip("/")
        #################
        # File handling #
        #################
        if is_file(self.path):
            self.path = "html" + self.path

            # Get Content-Type
            _,ext = os.path.splitext(self.path)
            # Open the file
            if CTYPE_ISBINARY[ext]:
                f = open(self.path, 'rb')#, errors='ignore')
            else:
                f = open(self.path)
            
            # Respond
            try:
                self.respond(200, [("Content-type",CTYPE_PATH[ext])], CTYPE_ISCACHE[ext])
            except KeyError:
                print("! Unhandled extension: "+ext)
                f.close()
                return

            # Send the file (encode if necessary)
            data = f.read()
            if type(data) == str:
                data = data.encode("UTF-8")
            self.wfile.write(data)
            f.close()
            return
        #################
        # *box handling #
        #################
        elif self.path.startswith("/box/"):
            self.respond(200,[("Content-type","text/html")])
            htgen.box(self.wfile, self.path[5:])
        
        ###################
        # Thread handling #
        ###################
        elif self.path.startswith("/thread/"):
            self.respond(200,[("Content-type","text/html")])
            htgen.thread(self.wfile, self.path[8:])
        
    def respond(self,code,headers=[],cache=False): # list of tuples
        self.send_response(code)
        for header in headers:
            self.send_header(header[0], header[1])
        if cache:
            self.send_header("Cache-Control","public; max-age=31536000")
        self.end_headers()
    
    # Silence terribly annoying stdout.
    def log_message(self, format, *args):
        return

def has_session_cookie(cookies):
    try:    
        c = cookies["Cookie"].value.split('=', 1)
        if c[0] == "session":
            return c[1]
    except KeyError:
        return False

FILE_PATTERN = re.compile(".*\.[a-zA-Z\d_]+$")
def is_file(path):
    if FILE_PATTERN.match(path):
        return True

def lacks_trailing_slash(path):
    return (("." not in path) and (not path.endswith("/")))

def run(server_class=HTTPServer, server_handler=RequestHandler):
    server_address = ("", 8000)
    httpd = server_class(server_address, server_handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.socket.close()
