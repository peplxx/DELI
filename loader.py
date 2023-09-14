from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data.database import db_session
from utils.utils import Notificator
from data import config


class Cleaner:
    def __init__(self):
        self.entity_list = {}

    def add(self, entity):
        if self.entity_list.get(entity.chat.id) is None:
            self.entity_list[entity.chat.id] = []
        self.entity_list[entity.chat.id] += [entity]

    async def clean(self, user_id):
        if user_id not in self.entity_list.keys():
            return 0
        for entity in self.entity_list[user_id]:
            try:
                await entity.delete()
            except:
                continue
        self.entity_list[user_id] = []

    async def send_message(self,message,*args,**kwargs):
        msg = await message.answer(*args,**kwargs)
        self.add(msg)


db_session.global_init("main.db")
session = db_session.create_session()
bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
cleaner = Cleaner()
notificator = Notificator(bot)
