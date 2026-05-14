import csv
import io
import urllib.request
import telebot
from telebot import types
import time
import sqlite3
from threading import Timer

days = {'Пн':'Понедельник', 'Вт':'Вторник','Ср':'Среда','Чт':'Четверг','Пт':'Пятница'}
dayss = ['Пн','Вт','Ср','Чт','Пт']
month = [str(i) for i in range(1,32)]

bot = telebot.TeleBot('TOKEN')
chanel = '-1003480826321'
admin_id = -5068105547

classes = {}
take_class = ['Дни', 'Уроки']
take_teacher = ['Альянаки', 'Антонова', 'Баталова', 'Бежина', 'Брюхов', 'Бушин', 'Вавилин',
                'Гасанов', 'Гачегова', 'Демидова', 'Жувак', 'Зотина', 'Ковалевская', 'Коровина',
                'Кощеева', 'Ларина', 'Леготкина', 'Мартынова', 'Митюшева', 'Нилов', 'Осташова', 'Ошева',
                'Полушкина', 'Разепина', 'Ракина', 'Рыкова', 'Снигирев', 'Соболева', 'Сонинский',
                'Степанова', 'Сутоцкая', 'Федотова', 'Филенко А', 'Филенко Д', 'Хайрулина', 'Хромцова',
                'Чепурин', 'Чигодайкина', 'Шестакова', 'Штейн']
teachers = dict.fromkeys(take_teacher, '')

def repeater(interval, function):
    Timer(interval, repeater, [interval, function]).start()
    function()

def information():
    global classes
    global take_class
    global teachers
    global take_teacher
    classes = {}
    teachers = dict.fromkeys(take_teacher, '')
    take_class = ['Дни', 'Уроки']
    url = "https://docs.google.com/spreadsheets/d/1NHZhfSniswd1ml4UmpXFy9Wg6ksReWAj/export?format=csv"
    response = urllib.request.urlopen(url)
    with io.TextIOWrapper(response, encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == 'Дни':
                for i in range(2,len(row)):
                    classes[row[i]] = f'{row[i]}'
                    take_class.append(row[i])
            else:
                if row[0] in month:
                    row[0] = ''
                elif row[0] in days:
                    for j in take_teacher:
                        teachers[j] = f'{teachers[j]}\n📆{days[row[0]]}\n'
                for i in range(2, len(row)):
                    classes[take_class[i]] = f'{classes[take_class[i]]}\n{row[0]}\n{row[1]}. {row[i]}'
                    for j in take_teacher:
                        if j in row[i]:
                            teachers[j] = f'{teachers[j]}\n{row[1]}. {row[i].split(j)[0]} {take_class[i]}\n'
                            break
        bot.send_message(admin_id, '✅Таблица обновлена.')

repeater(1800, information)

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type == 'private':
        conn = sqlite3.connect('students.db')
        cur = conn.cursor()
        cur.execute('SELECT user_id FROM users WHERE user_id = ?', (message.chat.id,))
        if cur.fetchone() == None:
            markup = types.InlineKeyboardMarkup(row_width=4)
            for i in range(2, len(take_class), 4):
                markup.add(types.InlineKeyboardButton(take_class[i], callback_data=f'S {take_class[i]}'),
                           types.InlineKeyboardButton(take_class[i + 1], callback_data=f'S {take_class[i + 1]}'),
                           types.InlineKeyboardButton(take_class[i + 2], callback_data=f'S {take_class[i + 2]}'),
                           types.InlineKeyboardButton(take_class[i + 3], callback_data=f'S {take_class[i + 3]}'))
            bot.send_message(message.chat.id, 'Добро пожаловать в Lyceum Bot 2.0!\n'
                                              'Выберите, пожалуйста, свой класс:', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, 'Добро пожаловать в Lyceum Bot 2.0!\n')
            markup = types.InlineKeyboardMarkup()
            markup1 = types.InlineKeyboardButton('📰Подписаться на канал', url='https://t.me/lupikprojects')
            markup2 = types.InlineKeyboardButton('✅Проверить подписку', callback_data='subscription')
            markup.add(markup1).row(markup2)
            bot.send_message(message.chat.id, 'Для использования бота необходимо быть подписанным на канал.',
                             reply_markup=markup)
        conn.commit()
        cur.close()
        conn.close()

@bot.message_handler(commands=['admin'])
def admin(message):
    if message.chat.id == admin_id:
        markup = types.InlineKeyboardMarkup(row_width=1)
        button1 = types.InlineKeyboardButton('💬Рассылка', callback_data='messages')
        button2 = types.InlineKeyboardButton('📲Скачать базу данных', callback_data='download')
        button_end = types.InlineKeyboardButton('❎Закрыть меню', callback_data='close')
        markup.add(button1,button2,button_end)
        bot.send_message(message.chat.id, 'Admin panel', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.message:
        if call.data == 'subscription':
            chat_member = bot.get_chat_member(chanel, call.message.chat.id)
            if chat_member.status in ['member', 'creator']:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                button1 = types.KeyboardButton('🗓Мое расписание')
                button2 = types.KeyboardButton('👩‍🏫Учителя')
                button3 = types.KeyboardButton('📂Классы')
                button4 = types.KeyboardButton('🔗Ссылка')
                button5 = types.KeyboardButton('⏰Звонки')
                button6 = types.KeyboardButton('⚙️Настройки')
                button7 = types.KeyboardButton('🆘Помощь')
                button8 = types.KeyboardButton('ℹ️О боте')
                markup.add(button1).row(button2, button3).row(button4,button5).row(button6).row(button7, button8)
                bot.delete_message(call.message.chat.id, call.message.message_id)
                bot.send_message(call.message.chat.id, 'Спасибо за подписку!', reply_markup=markup)
            else:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text='Вы не подписались')
                time.sleep(1)
                markup = types.InlineKeyboardMarkup()
                markup1 = types.InlineKeyboardButton('📰Подписаться на канал', url='https://t.me/lupikprojects')
                markup2 = types.InlineKeyboardButton('✅Проверить подписку', callback_data='subscription')
                markup.add(markup1).row(markup2)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text='Для использования бота необходимо быть подписанным на канал.',
                                      reply_markup=markup)

        elif call.data == 'close':
            bot.delete_message(call.message.chat.id, call.message.message_id)

        elif call.data[0] == 'S':
            conn = sqlite3.connect('students.db')
            cur = conn.cursor()
            cur.execute("INSERT INTO users (user_id, username, class) VALUES ('%s', '%s', '%s')" % (call.message.chat.id,call.message.chat.username, call.data[2:]))
            conn.commit()
            cur.close()
            conn.close()

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text='Класс успешно выбран!')
            markup = types.InlineKeyboardMarkup()
            markup1 = types.InlineKeyboardButton('📰Подписаться на канал', url='https://t.me/lupikprojects')
            markup2 = types.InlineKeyboardButton('✅Проверить подписку', callback_data='subscription')
            markup.add(markup1).row(markup2)
            bot.send_message(call.message.chat.id, 'Для использования бота необходимо быть подписанным на канал.',
                             reply_markup=markup)

        elif call.data[0] == '*':
            conn = sqlite3.connect('students.db')
            cur = conn.cursor()
            cur.execute("UPDATE users SET class = ? WHERE user_id = ?", (call.data[2:], call.message.chat.id))
            conn.commit()
            cur.close()
            conn.close()

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text='Класс успешно изменен!')

        elif call.data in take_class:
            vrem = classes[call.data]
            for i in days:
                vrem = vrem[:(vrem.index(i))]+'\n\n'+'📆'+days[i]+'\n'+vrem[(vrem.index(i)+2):]
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=f'Класс: {vrem}')

        elif call.data in take_teacher:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=f'Учитель: {call.data}\n{teachers[call.data]}')

        elif call.data[0] == '$':
            conn = sqlite3.connect('students.db')
            cur = conn.cursor()
            cur.execute('SELECT class, select_view FROM users WHERE user_id = ?', (call.message.chat.id,))
            vrem = cur.fetchone()
            clac = vrem[0]
            view = vrem[1]
            cur.close()
            conn.close()

            f = f'📅{days[call.data[1:]]}\n'

            if view == 'couples':
                f += '\n'
                if call.data == '$Пт':
                    strok = classes[clac].split(f'{dayss[dayss.index(call.data[1:])]}')[1]
                else:
                    strok = classes[clac].split(f'{dayss[dayss.index(call.data[1:]) + 1]}')[0].split(f'{dayss[dayss.index(call.data[1:])]}')[1]
                number = 1
                for i in range(1,11):
                    if i%2 != 0:
                        f += f'{number}. {strok.split(f'{i}.')[1].split(f'{i+1}.')[0]}'
                        number += 1
            else:
                if call.data == '$Пн':
                    f += classes[clac].split(f'{dayss[dayss.index(call.data[1:])+1]}')[0].split('Пн')[1]
                elif call.data == '$Пт':
                    f += classes[clac].split(f'{dayss[dayss.index(call.data[1:])]}')[1]
                else:
                    f += classes[clac].split(f'{dayss[dayss.index(call.data[1:]) + 1]}')[0].split(f'{dayss[dayss.index(call.data[1:])]}')[1]

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=f)

        elif call.data == 'feedback':
            msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Напишите, как можно подробнее, о ошибках с которыми вы столкнулись:\n\n'
                                                                                                       'Если передумали напишите - «Отмена»')
            bot.register_next_step_handler(msg, take_feedback)

        elif call.data == 'view':
            conn = sqlite3.connect('students.db')
            cur = conn.cursor()
            cur.execute('SELECT select_view FROM users WHERE user_id = ?', (call.message.chat.id,))
            typee = cur.fetchone()[0]
            cur.close()
            conn.close()

            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(types.InlineKeyboardButton('🔵Уроки', callback_data='lessons'), types.InlineKeyboardButton('🔴Пары', callback_data='couples'))
            if typee == 'couples':
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Выберите вид отображения занятий:\n\n'
                                                                                                     'Текущий: Пары\n\n'
                                                                                                     '‼️Вид меняется только для вкладки «🗓Мое расписание»', reply_markup=markup)
            else:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Выберите вид отображения занятий:\n\n'
                                                                                                     'Текущий: Уроки\n\n'
                                                                                                     '‼️Вид меняется только для вкладки «🗓Мое расписание»', reply_markup=markup)

        elif call.data == 'change':
            markup = types.InlineKeyboardMarkup(row_width=4)
            for i in range(2, len(take_class), 4):
                markup.add(types.InlineKeyboardButton(take_class[i], callback_data=f'* {take_class[i]}'),
                           types.InlineKeyboardButton(take_class[i + 1], callback_data=f'* {take_class[i + 1]}'),
                           types.InlineKeyboardButton(take_class[i + 2], callback_data=f'* {take_class[i + 2]}'),
                           types.InlineKeyboardButton(take_class[i + 3], callback_data=f'* {take_class[i + 3]}'))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Выберите, пожалуйста, свой класс:', reply_markup=markup)

        elif call.data == 'messages':
            msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Введите сообщение:')
            bot.register_next_step_handler(msg, send_messages)

        elif call.data in ['lessons', 'couples']:
            conn = sqlite3.connect('students.db')
            cur = conn.cursor()
            cur.execute("UPDATE users SET select_view = ? WHERE user_id = ?", (call.data, call.message.chat.id))
            conn.commit()
            cur.close()
            conn.close()
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Вид изменен.')

        elif call.data == 'download':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='⬇️База данных')
            with open("students.db", "rb") as f:
                bot.send_document(call.message.chat.id, f)

@bot.message_handler(content_types=['text'])
def bot_message(message):
    if message.chat.type == 'private':
        if bot.get_chat_member(chanel, message.chat.id).status in ['member', 'creator']:
            if message.text == '🗓Мое расписание' or message.text == '/get':
                markup = types.InlineKeyboardMarkup()
                b1 = types.InlineKeyboardButton('Понедельник', callback_data='$Пн')
                b2 = types.InlineKeyboardButton('Вторник', callback_data='$Вт')
                b3 = types.InlineKeyboardButton('Среда', callback_data='$Ср')
                b4 = types.InlineKeyboardButton('Четверг', callback_data='$Чт')
                b5 = types.InlineKeyboardButton('Пятница', callback_data='$Пт')
                markup.add(b1,b2).row(b3).row(b4,b5)
                bot.send_message(message.chat.id, 'Выберите день', reply_markup=markup)

            elif message.text == '👩‍🏫Учителя' or message.text == '/teacher':
                markup = types.InlineKeyboardMarkup(row_width=4)
                for i in range(0, len(take_teacher), 4):
                    if i != 36:
                        markup.add(types.InlineKeyboardButton(take_teacher[i], callback_data=f'{take_teacher[i]}'),
                               types.InlineKeyboardButton(take_teacher[i + 1], callback_data=f'{take_teacher[i + 1]}'),
                               types.InlineKeyboardButton(take_teacher[i + 2], callback_data=f'{take_teacher[i + 2]}'),
                               types.InlineKeyboardButton(take_teacher[i + 3], callback_data=f'{take_teacher[i + 3]}'))
                bot.send_message(message.chat.id, 'Выберите учителя', reply_markup=markup)

            elif message.text == '📂Классы' or message.text == '/class':
                markup = types.InlineKeyboardMarkup(row_width=4)
                for i in range(2, len(take_class), 4):
                    markup.add(types.InlineKeyboardButton(take_class[i], callback_data=f'{take_class[i]}'),
                               types.InlineKeyboardButton(take_class[i + 1], callback_data=f'{take_class[i + 1]}'),
                               types.InlineKeyboardButton(take_class[i + 2], callback_data=f'{take_class[i + 2]}'),
                               types.InlineKeyboardButton(take_class[i + 3], callback_data=f'{take_class[i + 3]}'))
                bot.send_message(message.chat.id, 'Выберите класс', reply_markup=markup)


            elif message.text == '🔗Ссылка' or message.text == '/link':
                bot.send_message(message.chat.id, 'Ссылка на таблицу с раписанием:\n'
                                                  'https://docs.google.com/spreadsheets/d/1NHZhfSniswd1ml4UmpXFy9Wg6ksReWAj')

            elif message.text == '⏰Звонки' or message.text == '/bells':
                photo = open('timetablejpg.jpg', 'rb')
                bot.send_photo(message.chat.id, photo)

            elif message.text == '🆘Помощь' or message.text == '/help':
                markup = types.InlineKeyboardMarkup(row_width=1)
                button1 = types.InlineKeyboardButton('❗️Сообщить о ошибке', callback_data='feedback')
                button2 = types.InlineKeyboardButton('❎Закрыть меню', callback_data='close')
                markup.add(button1,button2)
                bot.send_message(message.chat.id, 'Т.к. бот пишется энтузиастами, в свободное время, баги и ошибки более чем возможны.\n'
                                                  'Пожалуйста, сообщайте о багах по кнопке ниже, через бота, либо лично по <a href="t.me/lupiktg">ссылке</a>.', parse_mode='HTML', reply_markup=markup, disable_web_page_preview=True)

            elif message.text == 'ℹ️О боте' or message.text == '/about':
                markup = types.InlineKeyboardMarkup(row_width=1)
                button1 = types.InlineKeyboardButton('🔈Прочитать про бота', url='https://t.me/lupikprojects/11')
                button2 = types.InlineKeyboardButton('❎Закрыть меню', callback_data='close')
                markup.add(button1).row(button2)
                bot.send_message(message.chat.id, '<b>Lyceum Bot 2.0</b> - бот для удобного взаимодействия лицеистов с раписанием.\n\n'
                                                  'Расписание обновляется раз в 30 минут.\n'
                                                  'Бот написан на языке Python.\n'
                                                  'Подробнее по технической части <a href="https://t.me/lupikprojects/11">тут</a> (или по кнопке ниже)\n\n'
                                                  '👫Разработан бывшими учениками лицея:\n'
                                                  '├ <a href="t.me/lupiktg">Поезжаев Леонид</a>\n'
                                                  '└ <a href="t.me/sofiaivce">Загидуллина София</a>\n', parse_mode='HTML', disable_web_page_preview=True, reply_markup=markup)

            elif message.text == '⚙️Настройки' or message.text == '/settings':
                markup = types.InlineKeyboardMarkup(row_width=2)
                button1 = types.InlineKeyboardButton('👨‍🎓Класс', callback_data='change')
                button2 = types.InlineKeyboardButton('🧭Вид', callback_data='view')
                button3 = types.InlineKeyboardButton('❎Закрыть меню', callback_data='close')
                markup.add(button1,button2).row(button3)
                bot.send_message(message.chat.id, '⚙️Настройки\n\n'
                                                  '👨‍🎓Класс - сменить класс для отображения расписания\n\n'
                                                  '🧭Вид - поменять вид расписания (пары/уроки)', reply_markup=markup)

        else:
            markup = types.InlineKeyboardMarkup()
            markup1 = types.InlineKeyboardButton('📰Подписаться на канал', url='https://t.me/lupikprojects')
            markup2 = types.InlineKeyboardButton('✅Проверить подписку', callback_data='subscription')
            markup.add(markup1).row(markup2)
            bot.send_message(message.chat.id, 'Для использования бота необходимо быть подписанным на канал.',
                             reply_markup=markup)

def take_feedback(message):
    if message.text != 'отмена' and message.text != 'Отмена':
        msg = bot.forward_message(admin_id, message.chat.id, message.message_id)
        bot.reply_to(msg, '@lupiktg')
        bot.send_message(message.chat.id, '✅Сообщение отправлено!')
    else:
        bot.send_message(message.chat.id, '❌Отмена')

def send_messages(message):
    conn = sqlite3.connect('students.db')
    cur = conn.cursor()
    cur.execute('SELECT user_id, username FROM users')
    users = cur.fetchall()
    cur.close()
    conn.close()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('🗓Мое расписание')
    button2 = types.KeyboardButton('👩‍🏫Учителя')
    button3 = types.KeyboardButton('📂Классы')
    button4 = types.KeyboardButton('🔗Ссылка')
    button5 = types.KeyboardButton('⏰Звонки')
    button6 = types.KeyboardButton('⚙️Настройки')
    button7 = types.KeyboardButton('🆘Помощь')
    button8 = types.KeyboardButton('ℹ️О боте')
    markup.add(button1).row(button2, button3).row(button4, button5).row(button6).row(button7, button8)
    for i in users:
        try:
            bot.send_message(i[0], message.text, reply_markup=markup)
        except telebot.apihelper.ApiTelegramException:
            bot.send_message(admin_id, f'❌Ошибка отправки\n\n'
                                       f'Пользователь: @{i[1]}\n'
                                       f'Айди: <code>{i[0]}</code>', parse_mode='HTML')
    bot.send_message(admin_id, '✅Рассылка завершена.')

bot.infinity_polling(timeout=10, long_polling_timeout=5)