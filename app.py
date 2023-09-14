import sqlite3

from aiogram import executor
from loader import dp
from handlers.users import start,menu,profile

#async def on_startup(dispatcher):
    # Уведомляет про запуск

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
