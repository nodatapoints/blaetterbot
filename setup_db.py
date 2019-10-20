#!/usr/bin/python3.7

import sqlite3

con = sqlite3.connect('subscribers.db')

with con:
    con.executescript("""
    CREATE TABLE users(uid INTEGER PRIMARY KEY, subscriptions TEXT, init_msg INTEGER);
    CREATE TABLE lectures(shorthand INTEGER PRIMARY KEY, n INTEGER);
    """)

con.close()
