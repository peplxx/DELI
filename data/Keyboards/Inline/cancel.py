from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

cancel_keyboard = InlineKeyboardMarkup()
cancel_keyboard.add(InlineKeyboardButton("Cancel", callback_data='cancel_state'))
