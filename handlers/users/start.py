from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart

from data.config import quick_start
# Sqlite tables
from data.database.users import User
# Keyboards
from data.Keyboards.Inline.notification import notification
from handlers.users.menu import open_menu
from loader import cleaner, dp, session
from utils.utils import user_dict


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await cleaner.clean(message.chat.id)
    user_info = user_dict(message.from_user)
    search = session.query(User).filter(User.id == user_info['id']).first()
    await cleaner.send_message(message, quick_start, reply_markup=notification)
    if search is None:
        new_user = User()
        new_user.fill(*(user_info.values()))
        session.add(new_user)
        session.commit()
        await open_menu(message, clean=False)
    else:
        await open_menu(message, clean=False)



# TODO menu system
@dp.message_handler(commands=['cleaner'])
async def clean(message: types.Message):
    cleaner.add(message)
    await cleaner.clean(message.chat.id)


@dp.callback_query_handler(text="close", state="*")
async def close_message(query: types.CallbackQuery, state: FSMContext):
    await query.message.delete()

