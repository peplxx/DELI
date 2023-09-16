from aiogram import executor
from handlers.users import start,checks,profile,menu,group
from loader import dp

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
