from contextlib import contextmanager
import sqlite3
from operator import itemgetter

con = sqlite3.connect('subscribers.db', check_same_thread=False)

@contextmanager
def subscriptions(uid: int, init_msg_id=None):
    with con:
        cur = con.cursor()
        cur.execute('SELECT subscriptions FROM users WHERE uid=?', (uid,))
        row = cur.fetchone()
        if row is None:
            assert init_msg_id is not None
            cur.execute('INSERT INTO users VALUES (?, "", ?)', (uid, init_msg_id))
            subscr = set()

        else:
            subscr = set(row[0].split(','))

        yield subscr

        cur.execute('UPDATE users SET subscriptions=? WHERE uid=?', (','.join(subscr), uid))


def subscribed_users(lecture: str):
    cur = con.execute('SELECT uid FROM users WHERE instr(subscriptions, ?)', (lecture,))
    return map(itemgetter(0), cur)


def get_n(lecture: str):
    cur = con.execute('SELECT n FROM lectures WHERE id=?', (lecture,))
    return cur.fetchone()[0]

def increment_n(lecture: str):
    con.execute('UPDATE lectures SET n=n+1 WHERE id=?', (lecture,))
    con.commit()

def close_db_connection():
    con.close()
