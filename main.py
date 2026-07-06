from timetable import update_table, periodic_update
from aiogram import Bot, Dispatcher
from config import TOKEN, URL
from handlers import user
from admin import admin
import asyncio

async def main():
    bot = Bot(token=TOKEN)
    admin.bot = bot

    dp = Dispatcher()
    dp.include_router(user)
    dp.include_router(admin)

    await update_table(URL)
    asyncio.create_task(periodic_update())
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        print('Бот запущен.')
        asyncio.run(main())

    except KeyboardInterrupt:
        print('Бот выключен.')