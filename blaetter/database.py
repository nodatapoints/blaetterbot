from contextlib import contextmanager
import sqlite3

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
    cur = con.cursor()
    cur.execute('SELECT uid FROM users WHERE ? IN subscriptions', (lecture,))
    return cur
