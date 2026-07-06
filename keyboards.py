from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton,ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

async def choose_class():
    from timetable import take_class
    keyboard = InlineKeyboardBuilder()

    for i in range(2, len(take_class)):
        keyboard.add(InlineKeyboardButton(text=take_class[i], callback_data=f'class_{take_class[i]}'))

    return keyboard.adjust(4).as_markup()

async def choose_teacher():
    from timetable import take_teacher
    keyboard = InlineKeyboardBuilder()

    for teacher in take_teacher:
        keyboard.add(InlineKeyboardButton(text=teacher, callback_data=f'teacher_{teacher}'))

    return keyboard.adjust(4).as_markup()

async def another_classes():
    from timetable import take_class
    keyboard = InlineKeyboardBuilder()

    for i in range(2, len(take_class)):
        keyboard.add(InlineKeyboardButton(text=take_class[i], callback_data=f'check_{take_class[i]}'))

    return keyboard.adjust(4).as_markup()

async def choosing_new_class():
    from timetable import take_class
    keyboard = InlineKeyboardBuilder()

    for i in range(2, len(take_class)):
        keyboard.add(InlineKeyboardButton(text=take_class[i], callback_data=f'new_{take_class[i]}'))

    return keyboard.adjust(4).as_markup()


async def choose_weekday(selected_day = ''):
    another_color = ''
    days = {'Пн': another_color, 'Вт': another_color, 'Ср': another_color, 'Чт': another_color, 'Пт': another_color}
    days[selected_day] = 'success'

    choose_weekday = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Понедельник', callback_data='$Пн', style=days['Пн']),
             InlineKeyboardButton(text='Вторник', callback_data='$Вт', style=days['Вт'])],

            [InlineKeyboardButton(text='Среда', callback_data='$Ср', style=days['Ср'])],

            [InlineKeyboardButton(text='Четверг', callback_data='$Чт', style=days['Чт']),
             InlineKeyboardButton(text='Пятница', callback_data='$Пт', style=days['Пт'])]
        ]
    )
    return choose_weekday

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='🗓 Мое расписание')],
        [KeyboardButton(text='👩‍🏫 Учителя'), KeyboardButton(text='📂 Классы')],
        [KeyboardButton(text='🔗 Ссылка'), KeyboardButton(text='⏰ Звонки')],
        [KeyboardButton(text='⚙️ Настройки')],
        [KeyboardButton(text='🆘 Помощь'), KeyboardButton(text='ℹ️ О боте')],
    ],
    resize_keyboard=True
)

settings_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='👨‍🎓 Класс', callback_data='change_class'),
         InlineKeyboardButton(text='🧭 Вид', callback_data='change_view')]
    ]
)

types_of_timetable = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='🔵 Уроки', callback_data='type_lessons'),
         InlineKeyboardButton(text='🔴 Пары', callback_data='type_couples')]
    ]
)

report_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='❗️ Сообщить о ошибке',
                              url='https://t.me/lupiktg?text=Привет,%20я%20по%20поводу%20Lyceum%20Bot:%20')],
        [InlineKeyboardButton(text='🐱 GitHub',
                              url='https://github.com/leonidpoezzhaev/LyceumBot')]
    ]
)

work = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Клик',
                              url='https://t.me/lupiktg?text=Привет,%20я%20из%20Lyceum%20Bot.%20Нужна%20помощь')]
    ]
)

admin_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='💬 Рассылка', callback_data='messages')],
        [InlineKeyboardButton(text='📲 Скачать базу данных', callback_data='download')]
    ]
)

another_teacher_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='👨‍🏫 Другие учителя', callback_data='show_another_teacher')]
    ]
)

another_class_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='👥 Другие классы', callback_data='show_another_class')]
    ]
)

cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='❌ Отмена')]
    ]
)

skip_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Skip')],
        [KeyboardButton(text='❌ Отмена')]
    ],
    resize_keyboard=True
)

send_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='✅Отправить')],
        [KeyboardButton(text='❌ Отмена')]
    ],
    resize_keyboard=True
)