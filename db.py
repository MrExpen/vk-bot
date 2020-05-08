import sqlite3
import time

conn = sqlite3.connect("data.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS people(
    id INTEGER,
    vk_id INTEGER,
    first_name TEXT,
    last_name TEXT,
    nick_name TEXT,
    class INTEGER,
    for_what TEXT,
    exam TEXT,
    kind TEXT,
    time TEXT,
    message_id INTEGER
    )''')
c.execute('''CREATE TABLE IF NOT EXISTS id(
    id INTEGER
    )''')
c.execute('''CREATE TABLE IF NOT EXISTS mailing(
    id INTEGER,
    first INTEGER,
    second INTEGER,
    third INTEGER
    )''')

c.execute('''SELECT * FROM id''')
id = c.fetchone()
if id is None:
    id = 0
    with conn:
        c.execute('''INSERT INTO id VALUES(:id)''', {'id': id})
else:
    id = id[0]

def create_new_people(conn, c, user):
    global id
    c.execute('''SELECT * FROM mailing WHERE id=:id''', {'id': user['id']})
    user_mailing = c.fetchone()
    if user_mailing is None:
        with conn:
            c.execute('''INSERT INTO mailing VALUES(:id, :n, :n , :n)''', {'id': user['id'], 'n': 0})
    with conn:
        c.execute(
            '''INSERT INTO people VALUES(:id, :vk_id, :first_name, :last_name, :nick_name, :class, :for_what, :exam, :kind, :time, :message_id)''',
            {'id': id, 'vk_id': user['id'], 'first_name': user['first_name'], 'last_name': user['last_name'],
             'nick_name': None, 'class': None,
             'for_what': None, 'exam': None, 'kind': None, 'time': time.strftime("%Y.%m.%d %H:%M:%S", time.localtime()), 'message_id': None})
    id += 1
    with conn:
        c.execute('''UPDATE id SET id=:id''', {'id': id})