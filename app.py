

from aiogram import executor

from loader import dp

#async def on_startup(dispatcher):
    # Уведомляет про запуск

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
