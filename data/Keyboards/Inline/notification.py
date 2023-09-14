
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

notification = InlineKeyboardMarkup()
notification.add(InlineKeyboardButton("Close", callback_data='close'))
