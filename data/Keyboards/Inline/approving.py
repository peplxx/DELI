from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

approving = InlineKeyboardMarkup()

approving.add(InlineKeyboardButton("Approve", callback_data='approve'))
approving.add(InlineKeyboardButton("Cancel", callback_data='cancel_state'))
