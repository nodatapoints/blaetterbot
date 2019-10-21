#!/usr/bin/python3.7

import sqlite3
from blaetter import config
from pathlib import Path

db = Path('subscribers.db')
if db.exists():
    print('deleted db')
    db.unlink()  # delete the db

con = sqlite3.connect(db)

with con:
    con.executescript("""
    CREATE TABLE users(uid INTEGER PRIMARY KEY, subscriptions TEXT, init_msg INTEGER);
    CREATE TABLE lectures(id PRIMARY KEY, n INTEGER);
    """)
    args = ((lecture, ) for lecture in config['mirrors'])
    con.executemany('INSERT INTO lectures VALUES(?, 1)', args)

con.close()
