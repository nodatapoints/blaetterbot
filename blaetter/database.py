from contextlib import contextmanager
import sqlite3
from operator import itemgetter

con = sqlite3.connect('subscribers.db', check_same_thread=False)

@contextmanager
def subscriptions(uid: int):
    with con:
        cur = con.cursor()
        cur.execute('SELECT subscriptions FROM users WHERE uid=?', (uid,))
        comma_separated, = cur.fetchone()
        
        # use set() for '' the split otherwise
        subscr = set(comma_separated and comma_separated.split(','))

        yield subscr

        cur.execute('UPDATE users SET subscriptions=? WHERE uid=?', (','.join(subscr), uid))


def previous_start_message(uid: int):
    cur = con.cursor()
    cur.execute('SELECT init_msg FROM users WHERE uid=?', (uid,))
    res = cur.fetchone()
    return res and res[0]  # Return None if res == None, else res


def insert_new_user(uid: int, init_msg: int):
    con.execute('INSERT INTO users VALUES (?, "", ?)', (uid, init_msg))
    con.commit()

def update_init_msg(uid: int, init_msg: int):
    con.execute('UPDATE users SET init_msg=? WHERE uid=?', (uid, init_msg))
    con.commit()

def subscribed_users(lecture: str):
    cur = con.execute('SELECT uid FROM users WHERE instr(subscriptions, ?)', (lecture,))
    return map(itemgetter(0), cur)

def all_start_messages():
    cur = con.execute('SELECT uid, init_msg FROM users')
    yield from cur

def get_n(lecture: str):
    cur = con.execute('SELECT n FROM lectures WHERE id=?', (lecture,))
    return cur.fetchone()[0]

def increment_n(lecture: str):
    con.execute('UPDATE lectures SET n=n+1 WHERE id=?', (lecture,))
    con.commit()

def close_db_connection():  # TODO use me
    con.close()
