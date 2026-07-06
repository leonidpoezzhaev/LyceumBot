from aiogram.types import ReplyKeyboardRemove,InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.state import StatesGroup, State
from config import ADMIN_CHAT, ADMIN_USERNAME
from aiogram.fsm.context import FSMContext
from aiogram import Router, F, Bot
import keyboards as kb
import aiosqlite

admin = Router()
admin.bot = None

class send_message(StatesGroup):
    text = State()
    photo = State()
    button = State()
    is_good = State()

async def error_timetable(time, error):
    await admin.bot.send_message(ADMIN_CHAT, f'<b>Ошибка обновления таблицы!</b>\n\n'
                                             f'Время: <code>{time}</code>\n'
                                             f'Ошибка: <code>{error}</code>\n\n'
                                             f'Вызываю @{ADMIN_USERNAME} на помощь!', parse_mode='HTML')

@admin.message(F.text == '/admin')
async def admin_panel(message: Message):
    if message.chat.id == ADMIN_CHAT:
        await message.answer('Панель администратора',
                             reply_markup=kb.admin_keyboard)

@admin.callback_query(F.data == 'messages')
async def mailing(call: CallbackQuery, state: FSMContext):
    await state.set_state(send_message.text)
    await call.message.delete()
    await call.message.answer('Введите сообщение:', reply_markup= kb.cancel_keyboard)

@admin.message(send_message.text)
async def get_text(message: Message, state: FSMContext):
    if message.text == '❌ Отмена':
        await state.clear()
        await message.answer('❌ Отмена', reply_markup=ReplyKeyboardRemove())
        await message.answer('Панель администратора', reply_markup=kb.admin_keyboard)

    else:
        await state.update_data(text=message.html_text)
        await state.set_state(send_message.photo)
        await message.answer('Отправьте фото (если нужно)',
                             parse_mode='HTML', reply_markup=kb.skip_keyboard)


@admin.message(send_message.photo)
async def get_photo(message: Message, state: FSMContext):
    if message.text == '❌ Отмена':
        await state.clear()
        await message.answer('❌ Отмена', reply_markup=ReplyKeyboardRemove())
        await message.answer('Панель администратора', reply_markup=kb.admin_keyboard)
        return

    elif message.text == 'Skip':
        await state.update_data(photo='Skip')

    else:
        await state.update_data(photo=message.photo[-1].file_id)

    await state.set_state(send_message.button)
    await message.answer(
        'Отправьте кнопку в формате: <b>[Текст;Ссылка]</b> (или нет)',
        parse_mode='HTML', reply_markup=kb.skip_keyboard)


@admin.message(send_message.button)
async def end_mailing(message: Message, state: FSMContext):
    if message.text == '❌ Отмена':
        await state.clear()
        await message.answer('❌ Отмена', reply_markup=ReplyKeyboardRemove())
        await message.answer('Панель администратора', reply_markup=kb.admin_keyboard)
        return

    elif message.text == 'Skip':
        await state.update_data(button='Skip')

    else:
        await state.update_data(button=message.text)

    data = await state.get_data()
    await state.set_state(send_message.is_good)

    text, photo, button = data.values()

    if photo != 'Skip' and button != 'Skip':
        button_text, button_link = button.split(';')
        await message.answer_photo(caption=text, photo=photo, reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=button_text, url=button_link)]]), parse_mode='HTML')

    elif button != 'Skip':
        button_text, button_link = button.split(';')
        await message.answer(text=text, reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=button_text, url=button_link)]]), parse_mode='HTML')

    elif photo != 'Skip':
        await message.answer_photo(caption=text, photo=photo, parse_mode='HTML')

    else:
        await message.answer(text=text, parse_mode='HTML')

    await message.answer('Тестовое сообщение. Отправляем?', reply_markup=kb.send_keyboard)


@admin.message(send_message.is_good)
async def end_mailing(message: Message, state: FSMContext, bot: Bot):
    if message.text == '❌ Отмена':
        await state.clear()
        await message.answer('❌ Отмена', reply_markup=ReplyKeyboardRemove())
        await message.answer('Панель администратора', reply_markup=kb.admin_keyboard)
        return

    else:
        data = await state.get_data()
        await state.clear()
        text, photo, button = data.values()
        if button != 'Skip':
            button_text, button_link = button.split(';')

        async with aiosqlite.connect('students.db') as db:
            async with db.execute('SELECT user_id FROM users') as cur:
                take_data = await cur.fetchall()

        sended = 0
        not_sended = 0

        await message.answer('💬 Начинаю рассылку...', reply_markup=ReplyKeyboardRemove())

        for user_id in take_data:
            try:
                if photo != 'Skip' and button != 'Skip':
                    await bot.send_photo(chat_id=user_id[0], caption=text, photo=photo,
                                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                             [InlineKeyboardButton(text=button_text, url=button_link)]]), parse_mode='HTML')

                elif button != 'Skip':
                    await bot.send_message(chat_id=user_id[0], text=text,
                                           reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                               [InlineKeyboardButton(text=button_text, url=button_link)]]), parse_mode='HTML')

                elif photo != 'Skip':
                    await bot.send_photo(chat_id=user_id[0], caption=text, photo=photo, parse_mode='HTML')

                else:
                    await bot.send_message(chat_id=user_id[0], text=text, parse_mode='HTML')

                sended += 1

            except Exception as e:
                not_sended += 1

        await message.answer(f'✅ Рассылка завершена\n\n'
                             f'Сообщение доставлено <code>{sended}</code> пользователям\n\n'
                             f'<code>{not_sended}</code> пользователей не получили рассылку.',
                             parse_mode='HTML')

@admin.callback_query(F.data == 'download')
async def send_bigdata(call: CallbackQuery):
    await call.message.edit_text('⬇️')
    await call.message.answer_document(document=FSInputFile('students.db'))