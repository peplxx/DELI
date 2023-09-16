from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class GenerativeKeyboard:
    def __init__(self, data: list, close_button=False, *args, **kwargs):
        self.kb = InlineKeyboardMarkup(*args, **kwargs)
        # TODO limiting amount of buttons because we have limitations
        for button in data:
            if isinstance(button[0], list):
                buttons = []
                for elem in button:
                    buttons += [InlineKeyboardButton(f"{elem[0]}", callback_data=f'{elem[1]}')]
                self.kb.add(*buttons)
            else:
                self.kb.add(InlineKeyboardButton(f"{button[0]}", callback_data=f'{button[1]}'))
        if close_button:
            self.kb.add(InlineKeyboardButton("Close", callback_data='close'))
