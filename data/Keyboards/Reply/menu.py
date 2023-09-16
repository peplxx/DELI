from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)

menu = ReplyKeyboardMarkup(row_width=2)
menu.add(KeyboardButton('Profile👤'))
menu.add(*[KeyboardButton("Groups"),
           KeyboardButton('Checks')])
menu.add(*[KeyboardButton('Help'),
           KeyboardButton('About')])


profile_menu = ReplyKeyboardMarkup(row_width=2)
profile_menu.add("Profile Info")
profile_menu.add("Return to menu")

check_menu = ReplyKeyboardMarkup(row_width=2)
check_menu.add("Create check ➕")
check_menu.add("Show my checks")
check_menu.add("Return to menu")

group_menu = ReplyKeyboardMarkup(row_width=2)
group_menu.add(*["Create group","Join group"])
group_menu.add("My groups")
group_menu.add("Return to menu")

profile_options = InlineKeyboardMarkup(row_width=2)
profile_options.add(InlineKeyboardButton('Fill payment info',callback_data='fill_payment_info'))

profile_options.add(InlineKeyboardButton('Change username',callback_data="change_username"))
profile_options.add(InlineKeyboardButton('Return to menu', callback_data='return_to_menu'))