from functools import reduce

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from data.database.checks import Check
from data.database.groups import Group
# Sqlite tables
from data.database.users import User
# Keyboards
from data.Keyboards.Inline.cancel import cancel_keyboard
from data.Keyboards.Inline.generative_kb import GenerativeKeyboard
from data.Keyboards.Inline.notification import notification
from loader import cleaner, dp, notificator, session


class CHECKINPUT(StatesGroup):
    group_name = State()
    users = State()
    text = State()
    sum = State()


@dp.message_handler(commands=['make_check'])
async def group_name(message: types.Message):
    await cleaner.clean(message.chat.id)
    cleaner.add(message)
    # TODO Choosing group by clicking
    groups = [group for group in session.query(Group).all() if message.from_user.id in group.users]
    data = [(f"{group.name}", f"add_{group.name}") for group in groups]

    await cleaner.send_message(message, "Choose group name:",
                               reply_markup=GenerativeKeyboard(data, True).kb)


@dp.callback_query_handler(Text(contains='add_'))
async def enter_group(query: types.CallbackQuery, state: FSMContext):
    await cleaner.clean(query.message.chat.id)
    message = query.message
    group_name = query.data[4:]
    group = session.query(Group).filter(Group.name == group_name).first()
    if group is None:
        await message.answer("Nothing found!")
        await state.finish()
    else:
        await state.update_data(group_name=group_name)
        # parsing users from group
        users = [session.query(User).filter(User.id == group_user).first() for group_user in group.users]
        users_nocreator = [user for user in users if user.id != query.message.chat.id]
        creator = session.query(User).filter(User.id == query.message.chat.id).first()
        kb_data = [(f"{creator.username} ✅", f"mark_{0}:{creator.id}")]
        kb_data += [(f"{user.username} ❌", f"mark_{index}:{user.id}") for index, user in enumerate(users_nocreator, 1)]
        kb_data += [("Choose all", "choose_all_users"), ("Finish", "finish_choosing"), ("Cancel", 'cancel_state')]
        await cleaner.send_message(message, 'Choose users:', reply_markup=GenerativeKeyboard(kb_data).kb)
        await CHECKINPUT.users.set()


@dp.callback_query_handler(Text(contains='mark_'), state='*')
async def mark_user(query: types.CallbackQuery):
    button_index, user_id = map(int, query.data[len('mark_'):].split(':'))
    previous_data = query.message.reply_markup['inline_keyboard']
    new_data = [[data[0].text, data[0].callback_data] for data in previous_data]
    new_data[button_index][0] = new_data[button_index][0].replace('❌', '✅') if '❌' in new_data[button_index][0] \
        else new_data[button_index][0].replace('✅', '❌')
    await query.message.edit_reply_markup(GenerativeKeyboard(new_data).kb)


@dp.callback_query_handler(Text(contains="choose_all_users"), state='*')
async def mark_all_users(query: types.CallbackQuery):
    previous_data = query.message.reply_markup['inline_keyboard']
    new_data = [[data[0].text, data[0].callback_data] for data in previous_data]
    new_data = [[b[0].replace('❌', '✅') if '❌' in b[0] else b[0], b[1]] for b in new_data]
    try:
        await query.message.edit_reply_markup(GenerativeKeyboard(new_data).kb)
    except Exception:
        pass


@dp.callback_query_handler(Text(contains='finish_choosing'), state='*')
async def finish_choosing(query: types.CallbackQuery, state: FSMContext):
    await cleaner.clean(query.message.chat.id)
    data = [d[0].callback_data.split(':')[1] for d in query.message.reply_markup['inline_keyboard'] if
            d[0].text.count('✅')]
    await state.update_data(users=data)
    await cleaner.send_message(query.message, "Enter text of check:", reply_markup=cancel_keyboard)
    await CHECKINPUT.text.set()


@dp.message_handler(state=CHECKINPUT.text)
async def enter_check_text(message: types.Message, state: FSMContext):
    await cleaner.clean(message.chat.id)
    cleaner.add(message)
    await state.update_data(text=message.text)
    await cleaner.send_message(message, "Enter sum of check", reply_markup=cancel_keyboard)
    await CHECKINPUT.next()


@dp.message_handler(state=CHECKINPUT.sum)
async def enter_check_sum(message: types.Message, state: FSMContext):
    cleaner.add(message)
    await cleaner.clean(message.chat.id)
    try:
        amount = int(message.text)
        if amount > 1000000 or amount <= 0:
            raise ValueError
        await state.update_data(sum=amount)
        state_data = await state.get_data()
        group_name = state_data["group_name"]
        text = state_data["text"]
        session.query(Group).filter(Group.name == group_name).first()
        users = [int(user) for user in state_data['users']]
        new_check = Check()
        default_payed = [message.chat.id] if message.chat.id in users else []
        new_check.fill(text, amount, users, message.chat.id, payed=default_payed)
        session.add(new_check)
        session.commit()
        users = set(users)
        await notificator.notify_group(users, f"<b>New incoming check!</b>\n"
                                              f"From: <i>{message.from_user.full_name}</i>\n"
                                              f"Text: {text}\n"
                                              f"Your part: <b>{new_check.part}</b>р")

    except ValueError:
        await cleaner.send_message(message, "Incorrect format of sum", reply_markup=notification)
    await state.finish()


def created_check_msg(check):
    creator = session.query(User).filter(User.id == check.creator).first()
    users = set(check.users) - {creator.id}
    users_info = [[user, user in check.payed, session.query(User).filter(User.id == user).first()] for user in
                  users]
    users_text = reduce(lambda a, b: a + b,
                        [f"{info[2].username} {'[Payed]' if info[1] else '[Unpayed]'}\n" for info in
                         users_info])
    return [
        f"Check <i>#{check.id}</i>\n"
        f"Text: {check.text}\n"
        f"Total sum: {check.sum}р\n"
        f"Part: {check.part}р\n"
        f"\nUsers info:\n"
        f"{users_text}", GenerativeKeyboard([["Delete 🗑", f"delete_{check.id}"]]).kb]


@dp.callback_query_handler(Text(contains='_checks'))
async def show_checks(query: types.CallbackQuery):
    await cleaner.clean(query.message.chat.id)
    returning_kb = GenerativeKeyboard([['Back', 'my_checks']]).kb
    if query.data.split('_checks')[0] == 'incoming':

        user_id = query.message.chat.id
        checks = [check for check in session.query(Check).all() if
                  user_id in check.users and check.creator != user_id
                  and len(check.payed) != len(check.users)
                  and user_id not in check.payed]
        if len(checks) == 0:
            await cleaner.send_message(query.message, "There aren't any checks yet :(", reply_markup=returning_kb)
        else:
            await cleaner.send_message(query.message, "Here your incoming checks:",
                                       reply_markup=returning_kb)
        for check in checks:
            creator_name = session.query(User).filter(User.id == check.creator).first().username

            await cleaner.send_message(query.message,
                                       f"Check <i>#{check.id}</i>\n"
                                       f"From: {creator_name}\n"
                                       f"Text: {check.text}\n"
                                       f"Part: {check.part}р\n",
                                       reply_markup=GenerativeKeyboard([["Show payment info",
                                                                         f"show_payments_{check.id}"],
                                                                        ["Set as payed💵",
                                                                         f"ask_{check.id}:{user_id}:confirm"]]).kb)
    elif query.data.split('_checks')[0] == 'created':
        user_id = query.message.chat.id
        checks = [check for check in session.query(Check).all() if
                  check.creator == user_id and len(check.users) != len(check.payed)]
        if len(checks) == 0:
            await cleaner.send_message(query.message, "You haven't any created check!",
                                       reply_markup=returning_kb)
        else:
            await cleaner.send_message(query.message, "Here your created checks:",
                                       reply_markup=returning_kb)

        for check in checks:
            msg, reply = created_check_msg(check)
            await cleaner.send_message(query.message, msg, reply_markup=reply)


@dp.callback_query_handler(Text(contains="delete_"))
async def delete_check(query: types.CallbackQuery):
    check_id = int(query.data[7:])
    await query.message.edit_text("Are you sure to delete this check?",
                                  reply_markup=GenerativeKeyboard([[["Yes", f'forcedel_{check_id}'],
                                                                    ['No', f"canceldel_{check_id}"]]],
                                                                  row_width=2).kb)


@dp.callback_query_handler(Text(contains="forcedel_"))
async def force_delete_check(query: types.CallbackQuery):
    check_id = int(query.data[9:])
    check = session.query(Check).filter(Check.id == check_id).first()
    check.payed = check.users
    session.commit()
    await query.message.edit_text("Check was successfully deleted!")


@dp.callback_query_handler(Text(contains="canceldel_"))
async def cancel_delete_check(query: types.CallbackQuery):
    check_id = int(query.data[10:])
    check = session.query(Check).filter(Check.id == check_id).first()
    msg, reply = created_check_msg(check)
    await query.message.edit_text(msg, reply_markup=reply)


@dp.callback_query_handler(Text(contains='ask_'))
async def perform_ask_to_creator(query: types.CallbackQuery):
    info = query.data[4:].split(':')
    check_id, user_id, action = info
    check_id, user_id = int(check_id), int(user_id)
    check = session.query(Check).filter(Check.id == check_id).first()
    if check is None:
        await cleaner.send_message(query.message, "No check in db with this id!")
        return 0
    creator = check.creator
    user = session.query(User).filter(User.id == user_id).first()
    if action == "confirm":
        await query.message.edit_text("Request was sent to creator of check\n"
                                      "You will notified after his verification")
        await notificator.send(creator, f"<b><i>{user.username}</i></b> wants to confirm:\n"
                                        f"Check#{check.id}\n"
                                        f"Text:{check.text}\n"
                                        f"His part was:{check.part}",
                               reply_markup=GenerativeKeyboard([[["✅", f'confirm_check:{check.id}:{user.id}'],
                                                                 ["❌", f"decline_check:{check_id}:{user.id}"]]],
                                                               row_width=2).kb)


@dp.callback_query_handler(Text(contains="confirm_check"))
@dp.callback_query_handler(Text(contains="decline_check"))
async def perform_creator_answer(query: types.CallbackQuery):
    check_id, user_id = query.data[14:].split(':')
    check_id, user_id = int(check_id), int(user_id)
    check_id, user_id = int(check_id), int(user_id)
    check = session.query(Check).filter(Check.id == check_id).first()
    creator = session.query(User).filter(User.id == check.creator).first()
    if query.data.count('confirm_check'):
        if user_id not in check.payed:
            check.add_payed(user_id)
            session.commit()
        await notificator.send(user_id, f"<b>Your request was confirmed!</b>\n"
                                        f"Check#{check.id}\n"
                                        f"From: <i>{creator.username}</i>\n"
                                        f"Text: {check.text}\n"
                                        f"Your part was: {check.part}р\n")
    else:
        await notificator.send(user_id, f"<b>Your request was declined!</b>\n"
                                        f"Check#{check.id}\n"
                                        f"From: <i>{creator.username}</i>\n"
                                        f"Text: {check.text}\n"
                                        f"Your part was: {check.part}р\n")
    await query.message.delete()


@dp.callback_query_handler(Text(contains="show_payments_"))
async def show_payments(query: types.CallbackQuery):
    check_id = int(query.data.split('_')[2])
    check = session.query(Check).filter(Check.id == check_id).first()
    creator = session.query(User).filter(User.id == check.creator).first()
    previous_message = query.message
    if creator.number is not None and creator.bank is not None:
        prev_text = previous_message.text
        await previous_message.edit_text(prev_text + f"\n\n<b>- Payment information:</b>\n"
                                                     f"Number: <code>{creator.number}</code>\n"
                                                     f"Bank: {creator.bank}\n")
    else:
        prev_text = previous_message.text
        await previous_message.edit_text(prev_text + f"\n\n"
                                                     f"User don't fill payment info :(\n"
                                                     f"You can ask him directly\n"
                                                     f"His alias: @{creator.alias}\n")
    user_id = previous_message.chat.id
    await previous_message.edit_reply_markup(GenerativeKeyboard([["Set as payed💵",
                                                                  f"ask_{check.id}:{user_id}:confirm"]]).kb)
