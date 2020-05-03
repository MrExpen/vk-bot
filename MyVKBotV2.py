# -*- coding: utf-8 -*-

import vk_api
import random
import sqlite3
import time
import config
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


conn = sqlite3.connect("data.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS people(id INTEGER,
                                                vk_id INTEGER,
                                                first_name TEXT,
                                                last_name TEXT,
                                                nick_name TEXT,
                                                class INTEGER,
                                                for_what TEXT,
                                                exam TEXT,
                                                kind TEXT,
                                                time TEXT,
                                                message_id INTEGER)''')
c.execute('''CREATE TABLE IF NOT EXISTS id(id INTEGER)''')
c.execute('''CREATE TABLE IF NOT EXISTS mailing(
                                                id INTEGER,
                                                first INTEGER,
                                                second INTEGER,
                                                third INTEGER)''')

c.execute('''SELECT * FROM id''')
id = c.fetchone()
if id is None:
    id = 0
    with conn:
        c.execute('''INSERT INTO id VALUES(:id)''', {'id': id})
else:
    id = id[0]

vk_session = vk_api.VkApi(token=config.TOKEN)
longpoll = VkLongPoll(vk_session)


def parse_message(event):
    user = vk_session.method('users.get', {'user_id': event.user_id})[0]

    print("message from {0[first_name]} {0[last_name]}: {1.text}".format(user, event))
    c.execute('SELECT * FROM people WHERE vk_id=:vk_id', {'vk_id': user['id']})
    user_from_db = c.fetchall()
    if vk_session.method('groups.isMember', {'group_id': 181015479, 'user_id': user['id']}):
        if user_from_db != []:
            user_from_db = user_from_db[-1]
            if not user_from_db[10] is None:
                del_keyboard(user_from_db[10])
                with conn:
                    c.execute('''UPDATE people SET message_id=:message_id WHERE id=:id''',
                              {'id': user_from_db[0], 'message_id': None})

        if user_from_db == []:
            create_new_people(conn, c, user)
            vk_session.method('messages.send', {'user_id': user['id'], 'random_id': random.getrandbits(64),
                                                'message': 'Доброго времени суток!'})
            ask_for_name(user)
        elif event.text == 'Подать ещё одну заявку🆕':
            if not user_from_db[8] is None:
                create_new_people(conn, c, user)
                ask_for_name(user)
            else:
                vk_session.method('messages.send', {'user_id': user['id'], 'random_id': random.getrandbits(64),
                                                    'message': 'Вы не можете подать новую заявку пока не завершите заполнение этой😟.'})
        elif event.text == 'Рассылка📫':
            mailing(user, conn, c, user_from_db)
        elif event.text == 'first':
            c.execute('''SELECT * FROM mailing WHERE id=:id''', {'id': user['id']})
            user_mailing = c.fetchone()
            with conn:
                c.execute('''UPDATE mailing SET first=:first WHERE id=:id''',
                          {'id': user['id'], 'first': int(not bool(user_mailing[1]))})
            done(user)
        elif event.text == 'second':
            c.execute('''SELECT * FROM mailing WHERE id=:id''', {'id': user['id']})
            user_mailing = c.fetchone()
            with conn:
                c.execute('''UPDATE mailing SET second=:second WHERE id=:id''',
                          {'id': user['id'], 'second': int(not bool(user_mailing[2]))})
            done(user)
        elif event.text == 'third':
            c.execute('''SELECT * FROM mailing WHERE id=:id''', {'id': user['id']})
            user_mailing = c.fetchone()
            with conn:
                c.execute('''UPDATE mailing SET third=:third WHERE id=:id''',
                          {'id': user['id'], 'third': int(not bool(user_mailing[3]))})
            done(user)
        elif user_from_db[4] is None:
            if event.text != "К предыдущему вопросу🔙":
                if event.text != 'Начать' and not check_for_dig(event.text):
                    with conn:
                        c.execute('''UPDATE people SET nick_name=:nick_name WHERE id=:id''', {'id': user_from_db[0], 'nick_name': event.text})
                    ask_for_class(user)
                else:
                    invalid_value(user)
                    ask_for_name(user)
            else:
                ask_for_name(user)
        elif user_from_db[5] is None:
            if event.text != "К предыдущему вопросу🔙":
                try:
                    if 1 <= int(event.text) <= 11:
                        with conn:
                            c.execute('''UPDATE people SET class=:class WHERE id=:id''',
                                      {'id': user_from_db[0], 'class': event.text})
                        ask_for_what(user, c=c, conn=conn, user_from_db=user_from_db)

                    else:
                        invalid_value(user)
                        ask_for_class(user)
                except:
                    invalid_value(user)
                    ask_for_class(user)
            else:
                with conn:
                    c.execute('''UPDATE people SET nick_name=:nick_name WHERE id=:id''', {'id': user_from_db[0], 'nick_name': None})
                ask_for_name(user)
        elif user_from_db[6] is None:
            if event.text != "К предыдущему вопросу🔙":
                if event.text == 'Повышение качества знаний📚' or event.text == 'Подготовка к экзамену💯':
                    with conn:
                        c.execute('''UPDATE people SET for_what=:for_what WHERE id=:id''', {'id': user_from_db[0], 'for_what': event.text})
                    if event.text == 'Повышение качества знаний📚':
                        with conn:
                            c.execute('''UPDATE people SET exam=:exam WHERE id=:id''', {'id': user_from_db[0], 'exam': '-'})
                            c.execute('''UPDATE people SET kind=:kind WHERE id=:id''', {'id': user_from_db[0], 'kind': '-'})
                        thanq(user)
                    else:
                        if int(user_from_db[5]) < 10:
                            with conn:
                                c.execute('''UPDATE people SET exam=:exam WHERE id=:id''', {'id': user_from_db[0], 'exam': 'ОГЭ'})
                            ask_for_kind(user,conn, c, user_from_db)
                        else:
                            ask_for_exam(user, conn, c, user_from_db)
                else:
                    invalid_value(user)
                    ask_for_what(user, conn, c, user_from_db)
            else:
                with conn:
                    c.execute('''UPDATE people SET class=:class WHERE id=:id''', {'id': user_from_db[0], 'class': None})
                    c.execute('''UPDATE people SET exam=:exam WHERE id=:id''', {'id': user_from_db[0], 'exam': None})
                    c.execute('''UPDATE people SET kind=:kind WHERE id=:id''', {'id': user_from_db[0], 'kind': None})
                ask_for_class(user)
        elif user_from_db[7] is None:
            if event.text != "К предыдущему вопросу🔙":
                if event.text == "Базу" or event.text == "Профиль":
                    with conn:
                        c.execute('''UPDATE people SET exam=:exam WHERE id=:id''', {'id': user_from_db[0], 'exam': event.text})
                    ask_for_kind(user, conn, c, user_from_db)
                else:
                    invalid_value(user)
                    ask_for_exam(user, conn, c, user_from_db)
            else:
                with conn:
                    c.execute('''UPDATE people SET for_what=:for_what WHERE id=:id''', {'id': user_from_db[0], 'for_what': None})
                ask_for_exam(user, conn, c, user_from_db)

        elif user_from_db[8] is None:
            if event.text != "К предыдущему вопросу🔙":
                if event.text == 'Индивидуальные' or event.text == 'Групповые':
                    with conn:
                        c.execute('''UPDATE people SET kind=:kind WHERE id=:id''', {'id': user_from_db[0], 'kind': event.text})
                    thanq(user)
                else:
                    invalid_value(user)
                    ask_for_kind(user, conn, c, user_from_db)
            else:
                if int(user_from_db[5]) < 10:
                    with conn:
                        c.execute('''UPDATE people SET for_what=:for_what WHERE id=:id''', {'id': user_from_db[0], 'for_what': None})
                    ask_for_exam(user, conn, c, user_from_db)
                else:
                    with conn:
                        c.execute('''UPDATE people SET exam=:exam WHERE id=:id''', {'id': user_from_db[0], 'exam': None})
                        c.execute('''UPDATE people SET for_what=:for_what WHERE id=:id''', {'id': user_from_db[0], 'for_what': None})
                    ask_for_exam(user, conn, c, user_from_db)
        elif event.text == 'К предыдущему вопросу🔙':
            if user_from_db[6] == 'Повышение качества знаний📚':
                with conn:
                    c.execute('''UPDATE people SET for_what=:for_what WHERE id=:id''', {'id': user_from_db[0], 'for_what': None})
                    c.execute('''UPDATE people SET exam=:exam WHERE id=:id''', {'id': user_from_db[0], 'exam': None})
                    c.execute('''UPDATE people SET kind=:kind WHERE id=:id''', {'id': user_from_db[0], 'kind': None})
                ask_for_what(user, conn, c, user_from_db)
            else:
                with conn:
                    c.execute('''UPDATE people SET kind=:kind WHERE id=:id''', {'id': user_from_db[0], 'kind': None})
                ask_for_kind(user, conn, c, user_from_db)
        else:
            invalid_value(user, end=True)
    else:
        ask_for_podp(user)

def ask_for_name(user):
    keyboard = vk_api.keyboard.VkKeyboard()
    keyboard.add_button('Подать ещё одну заявку🆕', vk_api.keyboard.VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button('К предыдущему вопросу🔙', vk_api.keyboard.VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Рассылка📫', vk_api.keyboard.VkKeyboardColor.PRIMARY)
    vk_session.method('messages.send',
                      {'user_id': user['id'], 'random_id': random.getrandbits(64), 'message': 'Как Ваше имя?',
                       'keyboard': keyboard.get_keyboard()})

def ask_for_class(user):
    vk_session.method('messages.send',
                      {'user_id': user['id'], 'random_id': random.getrandbits(64), 'message': 'В каком Вы классе?'})

def ask_for_what(user, conn, c, user_from_db):
    keyboard = vk_api.keyboard.VkKeyboard(inline=True)
    keyboard.add_button("Повышение качества знаний📚", color=vk_api.keyboard.VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button("Подготовка к экзамену💯", color=vk_api.keyboard.VkKeyboardColor.POSITIVE)
    message_id = vk_session.method('messages.send', {'user_id': user['id'], 'random_id': random.getrandbits(64),
                                                      'message': 'Что Вас интересует?',
                                                      'keyboard': keyboard.get_keyboard()})
    with conn:
        c.execute('''UPDATE people SET message_id=:message_id WHERE id=:id''', {'id': user_from_db[0], 'message_id': message_id})

def ask_for_kind(user, conn, c, user_from_db):
    keyboard = vk_api.keyboard.VkKeyboard(inline=True)
    keyboard.add_button("Индивидуальные", color=vk_api.keyboard.VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button("Групповые", color=vk_api.keyboard.VkKeyboardColor.POSITIVE)
    message_id = vk_session.method('messages.send', {'user_id': user['id'], 'random_id': random.getrandbits(64),
                                                     'message': 'Какой тип занятий Вы предпочитаете?',
                                                     'keyboard': keyboard.get_keyboard()})
    with conn:
        c.execute('''UPDATE people SET message_id=:message_id WHERE id=:id''', {'id': user_from_db[0], 'message_id': message_id})

def ask_for_exam(user, conn, c, user_from_db):
    keyboard = vk_api.keyboard.VkKeyboard(inline=True)
    keyboard.add_button("Базу", color=vk_api.keyboard.VkKeyboardColor.POSITIVE)
    keyboard.add_button("Профиль", color=vk_api.keyboard.VkKeyboardColor.POSITIVE)
    message_id = vk_session.method('messages.send', {'user_id': user['id'], 'random_id': random.getrandbits(64),
                                                     'message': 'Какой вид экзамена по математике Вы планируете сдавать?',
                                                     'keyboard': keyboard.get_keyboard()})
    with conn:
        c.execute('''UPDATE people SET message_id=:message_id WHERE id=:id''', {'id': user_from_db[0], 'message_id': message_id})

def del_keyboard(message_id):
    message = vk_session.method('messages.getById', {'message_ids': message_id})['items'][0]
    keyboard = vk_api.keyboard.VkKeyboard()
    keyboard.add_button('Подать ещё одну заявку🆕', vk_api.keyboard.VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button('К предыдущему вопросу🔙', vk_api.keyboard.VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Рассылка📫', vk_api.keyboard.VkKeyboardColor.PRIMARY)
    vk_session.method('messages.edit', {'message': message['text'], 'message_id': message_id,
                                        'keyboard': keyboard.get_keyboard(),
                                        'peer_id': message['peer_id']})

def invalid_value(user, end=False):
    if not end:
        vk_session.method('messages.send', {'user_id': user['id'], 'message': 'Проверьте корректность введённых Вами данных🙅🙇.', 'random_id': random.getrandbits(64)})
    else:
        keyboard = vk_api.keyboard.VkKeyboard()
        keyboard.add_button('Подать ещё одну заявку🆕', vk_api.keyboard.VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('К предыдущему вопросу🔙', vk_api.keyboard.VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button('Рассылка📫', vk_api.keyboard.VkKeyboardColor.PRIMARY)
        vk_session.method('messages.send',
                          {'user_id': user['id'], 'message': 'Проверьте корректность введённых Вами данных🙅🙇.',
                           'random_id': random.getrandbits(64),
                           'keyboard': keyboard.get_keyboard()})

def thanq(user):
    keyboard = vk_api.keyboard.VkKeyboard()
    keyboard.add_button('Подать ещё одну заявку🆕',vk_api.keyboard.VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button('К предыдущему вопросу🔙', vk_api.keyboard.VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Рассылка📫', vk_api.keyboard.VkKeyboardColor.PRIMARY)
    vk_session.method('messages.send', {'user_id': user['id'], 'random_id': random.getrandbits(64),
                                        'message': 'Спасибо за обращение, наш преподаватель свяжется с Вами в ближайшее время😊.',
                                        'keyboard': keyboard.get_keyboard()})

def ask_for_podp(user):
    keyboard = vk_api.keyboard.VkKeyboard(one_time=True)
    keyboard.add_button('Начать', vk_api.keyboard.VkKeyboardColor.PRIMARY)
    vk_session.method('messages.send', {'user_id': user['id'], 'random_id': random.getrandbits(64),
                                        'message': 'Для начала подпишитесь на группу😋',
                                        'keyboard': keyboard.get_keyboard()})

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

def check_for_dig(text: str):
    for i in range(10):
        if text.find(str(i)) != -1:
            return True
    return False

def done(user):
    keyboard = vk_api.keyboard.VkKeyboard()
    keyboard.add_button('Подать ещё одну заявку🆕', vk_api.keyboard.VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button('К предыдущему вопросу🔙', vk_api.keyboard.VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Рассылка📫', vk_api.keyboard.VkKeyboardColor.PRIMARY)
    vk_session.method('messages.send', {'user_id': user['id'], 'random_id': random.getrandbits(64),
                                        'message': 'Успех!',
                                        'keyboard': keyboard.get_keyboard()})

def mailing(user, conn, c, user_from_db):
    keyboard = vk_api.keyboard.VkKeyboard(inline=True)
    c.execute('''SELECT * FROM mailing WHERE id=:id''', {'id': user['id']})
    user_mailing = c.fetchone()
    if user_mailing[1]:
        keyboard.add_button('first', vk_api.keyboard.VkKeyboardColor.POSITIVE)
    else:
        keyboard.add_button('first', vk_api.keyboard.VkKeyboardColor.NEGATIVE)
    if user_mailing[2]:
        keyboard.add_button('second', vk_api.keyboard.VkKeyboardColor.POSITIVE)
    else:
        keyboard.add_button('second', vk_api.keyboard.VkKeyboardColor.NEGATIVE)
    if user_mailing[3]:
        keyboard.add_button('third', vk_api.keyboard.VkKeyboardColor.POSITIVE)
    else:
        keyboard.add_button('third', vk_api.keyboard.VkKeyboardColor.NEGATIVE)
    message_id = vk_session.method('messages.send', {'user_id': user['id'], 'random_id': random.getrandbits(64),
                                        'message': 'Выберите на какую рассылку вы хотите подписаться.\n(Зелёный цвет означает что вы подписаны на эту рассылку)',
                                        'keyboard': keyboard.get_keyboard()})
    with conn:
        c.execute('''UPDATE people SET message_id=:message_id WHERE id=:id''', {'id': user_from_db[0], 'message_id': message_id})




for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            parse_message(event)
