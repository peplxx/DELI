from aiogram import Bot

from data.Keyboards.Inline.notification import notification


def user_dict(user_info):
    return {"id": user_info.id,
            "username":user_info.full_name,
            "name": user_info.first_name,
            "surname": user_info.last_name,
            "alias": user_info.username,
            }


class Notificator:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def send(self, user_id, message, reply_markup=notification):
        await self.bot.send_message(chat_id=user_id, text=message,
                              reply_markup=reply_markup)

    async def notify_group(self, group, message, reply_markup=notification):
        for user in group:
            await self.send(user, message, reply_markup)
