#!/usr/bin/env python

# This module performs database operations.

import sqlite3
import email

def connect():
    global cur
    global connection
    global close
    global connected
    connection = sqlite3.connect("data/mail.db")
    connection.isolation_level = None
    cur = connection.cursor()

def disconnect():
    connection.close()

def init():
    connect()
    cur.execute("CREATE TABLE IF NOT EXISTS Accounts (id INTEGER PRIMARY KEY, address TEXT UNIQUE,\
                                                      in_username TEXT, in_host TEXT, in_port INT,\
                                                      out_username TEXT, out_host TEXT, out_port INT)")
    cur.execute("CREATE TABLE IF NOT EXISTS Inbox (id TEXT UNIQUE, account INTEGER, data TEXT)")
    disconnect()

##################
# MAIN FUNCTIONS #
##################

# Account
#(id INTEGER PRIMARY KEY, address TEXT UNIQUE, in_username TEXT, in_host TEXT, in_port INT,
#                                              out_username TEXT, out_host TEXT, out_port INT)

def get_incoming_credentials(address):
    cur.execute("SELECT id,in_username,in_host,in_port FROM Accounts WHERE address = ?", (address,))
    return cur.fetchone()

def get_outgoing_credentials(address):
    cur.execute("SELECT id,out_username,out_host,out_port FROM Accounts WHERE address = ?", (address,))
    return cur.fetchone()

def add_account(address, in_username, in_host, in_port,
                    out_username, out_host, out_port):
    cur.execute("INSERT INTO Accounts (address,in_username,in_host,in_port,\
                                       out_username,out_host,out_port) VALUES(?,?,?,?,?,?,?)", (address,
                                                                                                in_username,
                                                                                                in_host,
                                                                                                in_port,
                                                                                                out_username,
                                                                                                out_host,
                                                                                                out_port))

def delete_account(address):
    cur.execute("DELETE FROM Accounts WHERE address = ?" (address,))


# Inbox
# (id TEXT UNIQUE, account INTEGER, data TEXT)

def add_raw_message(accid, rawdata):
    # Extract the Message-ID
    msgid = email.message_from_string(rawdata).get('Message-ID')
    cur.execute("INSERT OR IGNORE INTO Inbox (id,account,data) VALUES(?,?,?)", (msgid,accid,rawdata))

def delete_message(msgid):
    cur.execute("DELETE FROM Inbox WHERE msgid = ?",(msgid,))

