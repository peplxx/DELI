from aiogram import types
from aiogram.dispatcher.filters import Text

from data.database.groups import Group
# Keyboards
from data.Keyboards.Inline.generative_kb import GenerativeKeyboard
from data.Keyboards.Inline.notification import notification
from loader import cleaner, dp, session


@dp.message_handler(commands=['make_group'])
async def make_group(message: types.Message):
    await cleaner.clean(message.chat.id)
    cleaner.add(message)


def group_msg(group):
    return [
        f"{'Group Name:': <20}{group.name}\n"
        f"{'Group Id:': <26}{group.id}\n"
        f"{'Group Keyword:': <18}<code>{group.keyword}</code>\n"
        f"{'Admin:': <28}{group.admin}\n"
        f"Users: [{', '.join(group.users_names)}]",
        GenerativeKeyboard([['Return to menu', 'return_to_menu']]).kb]


@dp.callback_query_handler(Text(contains='show_group'))
async def show_group(query: types.CallbackQuery):
    group_id = int(query.data.split(':')[1])
    group = session.query(Group).filter(Group.id == group_id).first()
    msg, repl = group_msg(group)
    await query.message.answer(msg, reply_markup=notification)
