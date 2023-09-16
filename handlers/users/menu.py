from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

# DataBase classes
from data.database.groups import Group
from data.database.users import User
from data.Keyboards.Inline.cancel import cancel_keyboard
from data.Keyboards.Inline.generative_kb import GenerativeKeyboard
from data.Keyboards.Inline.notification import notification
# Keyboards
from data.Keyboards.Reply.menu import (check_menu, group_menu, menu,
                                       profile_menu)
from loader import cleaner, dp, notificator, session
from utils.utils import user_dict


class INPUT(StatesGroup):
    # isortTODO Better naming of states
    keyword = State()
    group_name = State()


@dp.message_handler(state=INPUT.keyword)
async def user_to_group(message: types.Message, state: FSMContext):
    await cleaner.clean(message.chat.id)
    cleaner.add(message)
    group = session.query(Group).filter(Group.keyword == message.text).first()
    user_info = user_dict(message.from_user)
    newcomer = session.query(User).filter(User.id == user_info['id']).first()
    if group is None:
        await cleaner.send_message(message, "Nothing found!")
    elif user_info['id'] in group.users:
        await cleaner.send_message(message, 'You are already in this group!')
    elif len(newcomer.groups) == newcomer.grouplimit:
        await cleaner.send_message(message, "You have reached max groups limit!")
    elif len(group.users) == group.max_users:
        await cleaner.send_message(message, 'This group have reached max users limit!')
    else:
        await notificator.notify_group(group.users, f"New member in {group.name}!\n"
                                                    f"Username: {message.chat.full_name}\n"
                                                    f"Alias: @{user_info['alias']}")
        group.add_user(user_info['id'])
        newcomer.add_group(group.id)
        session.commit()
        await message.answer(f"Successfully joined to group!\n\n"
                             f"Group Name: {group.name}")

        # TODO Normal user notification format

    await state.finish()


@dp.message_handler(Text(contains="Join group"))
@dp.message_handler(commands=['join'])
async def join_into_group(message: types.Message):
    cleaner.add(message)
    await cleaner.send_message(message, 'Enter group keyword:', reply_markup=cancel_keyboard)
    await INPUT.keyword.set()


def group_msg(group):
    return [
        f"{'Group Name:': <20}{group.name}\n"
        f"{'Group Id:': <26}{group.id}\n"
        f"{'Group Keyword:': <18}<code>{group.keyword}</code>\n"
        f"{'Admin:': <28}{group.admin}\n"
        f"Users: [{', '.join(group.users_names)}]",
        GenerativeKeyboard([['Return to menu', 'return_to_menu']]).kb]


@dp.message_handler(state=INPUT.group_name)
async def make_group(message: types.Message, state: FSMContext):
    await cleaner.clean(message.chat.id)
    cleaner.add(message)
    user_info = user_dict(message.from_user)
    group_name = message.text
    new_group = Group()
    new_group.fill(user_info['id'], group_name)
    session.add(new_group)
    creator = session.query(User).filter(User.id == message.chat.id).first()
    creator.add_group(group_id=new_group.id)
    session.commit()

    'Group was created successfully!\n\n'
    groupmasg, reply = group_msg(new_group)
    await message.answer('Group was created successfully!\n\n' + groupmasg,
                         reply_markup=reply)
    await state.finish()


@dp.message_handler(commands=["help"])
@dp.message_handler(Text(contains='Help'))
@dp.message_handler(Text(contains="About"))
async def not_implemented(message: types.Message):
    await message.answer("Not implemented yet :(",
                         reply_markup=notification)
    await open_menu(message)


@dp.message_handler(commands=['menu'])
@dp.message_handler(Text(contains='Return to menu'))
async def open_menu(message: types.Message, clean=True):
    if clean:
        cleaner.add(message)
        await cleaner.clean(message.chat.id)
    await cleaner.send_message(message, "Main menu:", reply_markup=menu)


@dp.callback_query_handler(Text(contains="return_to_menu"))
async def open_menu_callback(query: types.CallbackQuery):
    await open_menu(query.message)


@dp.callback_query_handler(text='cancel_state', state="*")
async def cancel_state(query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await open_menu(query.message)


@dp.message_handler(Text(contains='Profile👤'))
async def open_profile(message: types.Message):
    cleaner.add(message)
    await cleaner.clean(message.chat.id)
    await cleaner.send_message(message, "Profile menu:", reply_markup=profile_menu)


@dp.callback_query_handler(Text(contains='group_menu'))
async def cbshow_group_menu(query: types.CallbackQuery):
    await show_group_menu(query.message)


@dp.message_handler(Text(contains='Groups'))
async def show_group_menu(message: types.Message):
    cleaner.add(message)
    await cleaner.clean(message.chat.id)
    await cleaner.send_message(message, "Group menu:", reply_markup=group_menu)


@dp.callback_query_handler(Text(contains="check_menu"))
async def cbshow_check_menu(query: types.CallbackQuery):
    await show_check_menu(query.message)


@dp.message_handler(Text(contains='Checks'))
async def show_check_menu(message: types.Message):
    cleaner.add(message)
    await cleaner.clean(message.chat.id)
    await cleaner.send_message(message, "Check menu:", reply_markup=check_menu)


@dp.callback_query_handler(Text(contains="my_checks"))
async def cbshow_cheks(query: types.CallbackQuery):
    await show_checks(query.message)


@dp.message_handler(Text(contains="Show my checks"))
async def show_checks(message: types.Message):
    cleaner.add(message)
    await cleaner.clean(message.chat.id)
    await cleaner.send_message(message, "Here you can see your checks:",
                               reply_markup=GenerativeKeyboard([['Incoming checks', 'incoming_checks'],
                                                                ["Created checks", 'created_checks'],
                                                                ["Back", 'check_menu']]).kb)


@dp.message_handler(Text(contains="Create check"))
async def create_check(message: types.Message):
    await cleaner.clean(message.chat.id)
    cleaner.add(message)
    groups = [group for group in session.query(Group).all() if message.from_user.id in group.users]
    data = [(f"{group.name}", f"add_{group.name}") for group in groups]
    data += [["Cancel", 'cancel_state']]
    await cleaner.send_message(message, "Choose group name:",
                               reply_markup=GenerativeKeyboard(data).kb)


@dp.message_handler(Text(contains="Create group"))
async def create_group(message: types.Message):
    await cleaner.clean(message.chat.id)
    cleaner.add(message)
    user = session.query(User).filter(User.id == message.chat.id).first()
    if len(user.groups) < int(user.grouplimit):
        await cleaner.send_message(message, "Enter group name:", reply_markup=cancel_keyboard)
        await INPUT.group_name.set()
    else:
        await cleaner.send_message(message, "You have reached max group limit!", reply_markup=notification)


@dp.message_handler(Text(contains="My groups"))
async def show_my_groups(message: types.Message):
    await cleaner.clean(message.chat.id)
    cleaner.add(message)
    user = session.query(User).filter(User.id == message.chat.id).first()
    groups = [session.query(Group).filter(Group.id == curr).first() for curr in user.groups]
    print([group.admin for group in groups])
    data = [[f"{group.name} {'[OWNER]' if group.admin == message.chat.id else ''}",
             f'show_group:{group.id}'] for group in groups]
    data.append(["Back", "group_menu"])
    await cleaner.send_message(message, "Here your groups:",
                               reply_markup=GenerativeKeyboard(data).kb)


class USERNAME(StatesGroup):
    input = State()


@dp.callback_query_handler(Text(contains="change_username"))
async def change_username(query: types.CallbackQuery):
    cleaner.add(query.message)
    await cleaner.clean(query.message.chat.id)
    await cleaner.send_message(query.message, "Enter your new username:",
                               reply_markup=cancel_keyboard)
    await USERNAME.input.set()


@dp.message_handler(state=USERNAME.input)
async def apply_changing(message: types.Message, state: FSMContext):
    await cleaner.clean(message.chat.id)
    cleaner.add(message)
    new_username = message.text
    user = session.query(User).filter(User.id == message.chat.id).first()
    user.username = new_username
    session.commit()
    await cleaner.send_message(message, "Username was changed!")
    await open_menu(message)
    await state.finish()
