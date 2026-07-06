from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart
from aiogram import Router, F
from timetable import days
import keyboards as kb
import aiosqlite

user = Router()

@user.message(CommandStart())
async def start_bot(message: Message):
    async with aiosqlite.connect('students.db') as db:
        async with db.execute('SELECT user_id FROM users WHERE user_id = ?', (message.chat.id,)) as cur:
            data = await cur.fetchone()

    keyboard = await kb.choose_class()

    if data is None:
        await message.answer('Добро пожаловать в Lyceum Bot 2.0!\n'
                             'Выберите, пожалуйста, свой класс:',
                             reply_markup=keyboard)
    else:
        await message.answer('Добро пожаловать в Lyceum Bot 2.0!',
                             reply_markup=kb.main_menu)

@user.callback_query(F.data.startswith('class_'))
async def class_selected(call: CallbackQuery):
    async with aiosqlite.connect('students.db') as db:
        await db.execute("INSERT INTO users (user_id, username, class) VALUES ('%s', '%s', '%s')" % (call.message.chat.id, call.message.chat.username, call.data.split('_')[1]))
        await db.commit()
    await call.message.edit_text('Класс успешно выбран!')
    await call.message.answer('Добро пожаловать в Lyceum Bot 2.0!',
                              reply_markup=kb.main_menu)

@user.message((F.text == '/get') | (F.text == '🗓 Мое расписание'))
async def my_timetable(message: Message):
    keyboard = await kb.choose_weekday()
    await message.answer('Выберите день:', reply_markup=keyboard)

@user.callback_query(F.data.startswith('$'))
async def day_selected(call: CallbackQuery):
    from timetable import classes

    async with aiosqlite.connect('students.db') as db:
        async with db.execute('SELECT class, select_view FROM users WHERE user_id = ?', (call.message.chat.id,)) as cur:
            temp = await cur.fetchone()

    clac, view = temp
    dayss = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт']

    text = f'<b>📅 {days[call.data[1:]]}</b>\n'

    if view == 'couples':
        text += '\n'
        if call.data == '$Пт':
            strok = classes[clac].split(f'{dayss[dayss.index(call.data[1:])]}')[1]
        else:
            strok = classes[clac].split(f'{dayss[dayss.index(call.data[1:]) + 1]}')[0].split(
                f'{dayss[dayss.index(call.data[1:])]}')[1]
        number = 1
        for i in range(1, 11):
            if i % 2 != 0:
                text += f'<b>{number}.</b> {strok.split(f'{i}.')[1].split(f'{i + 1}.')[0]}'
                number += 1

    else:
        if call.data == '$Пн':
            text += classes[clac].split(f'{dayss[dayss.index(call.data[1:]) + 1]}')[0].split('Пн')[1]

        elif call.data == '$Пт':
            text += classes[clac].split(f'{dayss[dayss.index(call.data[1:])]}')[1]

        else:
            text += classes[clac].split(f'{dayss[dayss.index(call.data[1:]) + 1]}')[0].split(f'{dayss[dayss.index(call.data[1:])]}')[1]

        for number in range(1,11):
            text = text.replace(f'{number}.', f'<b>{number}.</b>')

    keyboard = await kb.choose_weekday(call.data[1:])

    await call.message.edit_text(text, reply_markup=keyboard, parse_mode='HTML')

@user.message((F.text == '👩‍🏫 Учителя') | (F.text == '/teacher'))
async def teacher_timetable(message: Message):
    keyboard = await kb.choose_teacher()
    await message.answer('Выберите учителя:', reply_markup=keyboard)

@user.callback_query(F.data.startswith('teacher_'))
async def teacher_selected(call: CallbackQuery):
    from timetable import teachers
    teacher = call.data.split('_')[1]
    await call.message.edit_text(f'<b>Учитель:</b> <code>{teacher}</code>\n{teachers[teacher]}',
                                 parse_mode='HTML', reply_markup=kb.another_teacher_keyboard)

@user.callback_query(F.data == 'show_another_teacher')
async def another_teacher(call: CallbackQuery):
    keyboard = await kb.choose_teacher()
    await call.message.edit_text(text='Выберите другого учителя:', reply_markup=keyboard)

@user.message((F.text == '📂 Классы') | (F.text == '/class'))
async def check_another_class(message: Message):
    keyboard = await kb.another_classes()
    await message.answer('Выберите класс:', reply_markup=keyboard)

@user.callback_query(F.data.startswith('check_'))
async def another_class_selected(call: CallbackQuery):
    from timetable import classes
    text = classes[call.data.split('_')[1]]
    text = text.replace(call.data.split('_')[1], f'<code>{call.data.split('_')[1]}</code>')

    for i in days:
        text = text[:(text.index(i))] + '\n\n' + '<b>📆' + days[i] + '</b>\n' + text[(text.index(i) + 2):]

    for number in range(1, 11):
        text = text.replace(f'{number}.', f'<b>{number}.</b>')

    await call.message.answer(f'<b>Класс:</b> {text}', parse_mode='HTML', reply_markup=kb.another_class_keyboard)

@user.callback_query(F.data == 'show_another_class')
async def another_teacher(call: CallbackQuery):
    keyboard = await kb.another_classes()
    await call.message.edit_text(text='Выберите другой класс:', reply_markup=keyboard)

@user.message((F.text == '🔗 Ссылка') | (F.text == '/link'))
async def timetable_link(message: Message):
    await message.answer('Ссылка на таблицу с раписанием:\n'
                         'https://docs.google.com/spreadsheets/d/1NHZhfSniswd1ml4UmpXFy9Wg6ksReWAj')

@user.message((F.text == '⏰ Звонки') | (F.text == '/bells'))
async def bell_timetable(message: Message):
    await message.answer_photo(photo=FSInputFile('src/bells_timetable.jpg'))

@user.message((F.text == '⚙️ Настройки') | (F.text == '/settings'))
async def settings(message: Message):
    await message.answer('⚙️Настройки:\n\n'
                         '👨‍🎓 Класс - сменить класс для отображения расписания\n\n'
                         '🧭 Вид - поменять вид расписания (пары/уроки)',
                         reply_markup=kb.settings_menu)

@user.callback_query(F.data == 'change_class')
async def change_class(call: CallbackQuery):
    keyboard = await kb.choosing_new_class()
    await call.message.edit_text('Выберите новый класс:', reply_markup=keyboard)

@user.callback_query(F.data.startswith('new_'))
async def new_class_selected(call: CallbackQuery):
    async with aiosqlite.connect('students.db') as db:
        await db.execute("UPDATE users SET class = ? WHERE user_id = ?", (call.data.split('_')[1], call.message.chat.id))
        await db.commit()

    await call.message.edit_text('Класс успешно изменен!')

@user.callback_query(F.data == 'change_view')
async def choise_type(call: CallbackQuery):
    async with aiosqlite.connect('students.db') as db:
        async with db.execute('SELECT select_view FROM users WHERE user_id = ?', (call.message.chat.id,)) as cur:
            selected_type = await cur.fetchone()

    if selected_type[0] == 'couples':
        selected_type = 'Пары'
    else:
        selected_type = 'Уроки'

    await call.message.edit_text(f'Выберите вид отображения занятий:\n\n'
                                 f'Текущий: <code>{selected_type}</code>\n\n'
                                 f'‼️ Вид меняется только для вкладки «🗓 Мое расписание»',
                                 reply_markup=kb.types_of_timetable, parse_mode='HTML')

@user.callback_query(F.data.startswith('type_'))
async def new_type_timetable(call: CallbackQuery):
    async with aiosqlite.connect('students.db') as db:
        await db.execute("UPDATE users SET select_view = ? WHERE user_id = ?", (call.data.split('_')[1], call.message.chat.id))
        await db.commit()
    await call.message.edit_text('Вид успешно изменен!')

@user.message((F.text == '🆘 Помощь') | (F.text == '/help'))
async def need_help(message: Message):
    await message.answer('<b>Нашли ошибку или есть предложения по улучшению?</b>\n\n'
                         'Отлично! Смело обращайтесь в личку по кнопке ниже или отправляйте Pull request на <a href="https://github.com/leonidpoezzhaev/LyceumBot">гит хабе</a>.\n\n'
                         'Сделаем лучшее вместе!', reply_markup=kb.report_keyboard, parse_mode='HTML', disable_web_page_preview=True)

@user.message((F.text == 'ℹ️ О боте') | (F.text == '/about'))
async def about_bot(message:Message):
    await message.answer('<b>🤖 Lyceum Bot</b> · <code>2.0</code>\n\n'
                         ''
                         '<b>👤 Разработка</b>\n'
                         '├ <b>Разработчик:</b> @lupiktg\n'
                         '└ <b>Муза:</b> @fofisofia8\n\n'
                         ''
                         '<b>⚙️ Технологии</b>\n'
                         '├ <b>Язык:</b> Python 3.14\n'
                         '├ <b>Фреймворк:</b> Aiogram 3.25\n'
                         '└ <b>БД:</b> SQLite\n\n'
                         ''
                         '<b>🧾 Контакты</b>\n'
                         '├ <b>ТГ Канал:</b> @lupikdev\n'
                         '└ <b>GitHub:</b> github.com/leonidpoezzhaev/LyceumBot\n\n'
                         ''
                         '<b>📚 Библиотеки</b>\n'
                         '<blockquote>aiogram, aiosqlite, aiohttp, asyncio, csv, io, datetime</blockquote>\n\n'
                         ''
                         '<tg-spoiler>Нужен свой бот Telegram или решение лабораторной задачи? Жми по кнопке ниже, сделаю быстро и за приемлемую цену.</tg-spoiler>',
                         reply_markup=kb.work, parse_mode='HTML', disable_web_page_preview=True)