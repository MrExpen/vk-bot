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

def user_from_data(user):
    global id
    c.execute('SELECT * FROM people WHERE vk_id=:vk_id', {'vk_id': user['id']})
    user_from_db = c.fetchall()
    if user_from_db:
        user_from_db = user_from_db[-1]
        return {
            'id': user_from_db[0],
            'nick_name': user_from_db[4],
            'class': user_from_db[5],
            'for_what': user_from_db[6],
            'exam': user_from_db[7],
            'kind': user_from_db[8],
            'time': user_from_db[9],
        }
    with conn:
        c.execute(
            '''INSERT INTO people VALUES(:id, :vk_id, :first_name, :last_name, :nick_name, :class, :for_what, :exam, :kind, :time)''',
            {'id': id, 'vk_id': user['id'], 'first_name': user['first_name'], 'last_name': user['last_name'],
             'nick_name': None, 'class': None,
             'for_what': None, 'exam': None, 'kind': None, 'time': time.strftime("%Y.%m.%d %H:%M:%S", time.localtime())})
    