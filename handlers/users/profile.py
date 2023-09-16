
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from data.database.users import User
from data.Keyboards.Inline.approving import approving
from data.Keyboards.Inline.cancel import cancel_keyboard
from data.Keyboards.Reply.menu import menu, profile_options
from loader import cleaner, dp, session
from utils.utils import user_dict


@dp.message_handler(Text(contains="Profile Info"))
async def show_profile_info(message: types.Message):
    await cleaner.clean(message.chat.id)
    cleaner.add(message)
    user = session.query(User).filter(User.id == message.chat.id).first()
    payment_filled = user.number != 'None'
    await cleaner.send_message(message,
                               f"Here your profile info:\n"
                               f"<b>[General info]</b>\n"
                               f"Your username: {user.username}\n"
                               f"\n<b>[Payment info]</b>\n"
                               f"(For your checks only)\n"
                               f"{f'<code>{user.number}</code> | {user.bank}' if payment_filled else 'You do not fill payment info!'}",
                               reply_markup=profile_options)


class PAYMENT(StatesGroup):
    number = State()
    bank = State()


@dp.callback_query_handler(Text(contains='fill_payment_info'))
async def fill_payment_info(query: types.CallbackQuery):
    message = query.message
    await cleaner.clean(message.chat.id)
    cleaner.add(message)
    await cleaner.send_message(message, "Enter your phone number:", reply_markup=cancel_keyboard)
    await PAYMENT.number.set()


@dp.message_handler(state=PAYMENT.number)
async def fill_phone_number(message: types.Message, state: FSMContext):
    await cleaner.clean(message.chat.id)
    cleaner.add(message)
    # TODO number validation
    await cleaner.send_message(message, "Enter your bank:", reply_markup=cancel_keyboard)
    await state.update_data(number=message.text)
    await PAYMENT.next()


@dp.message_handler(state=PAYMENT.bank)
async def fill_bank(message: types.Message, state: FSMContext):
    await cleaner.clean(message.chat.id)
    cleaner.add(message)
    info = await state.get_data()
    await state.update_data(bank=message.text)
    await cleaner.send_message(message, f'Here your payment info:\n'
                                        f'Number: <code>{info["number"]}</code>\n'
                                        f'Bank: {message.text}', reply_markup=approving)


@dp.callback_query_handler(Text(contains='approve'), state=PAYMENT.bank)
async def approve_bank_info(query: types.CallbackQuery, state: FSMContext):
    await cleaner.clean(query.message.chat.id)
    user_info = user_dict(query.message.chat)
    user = session.query(User).filter(User.id == user_info['id']).first()
    state_data = await state.get_data()
    user.bank = state_data['bank']
    user.number = state_data['number']
    session.commit()
    await cleaner.send_message(query.message, "Payment info was refreshed!")
    await state.finish()
    await cleaner.send_message(query.message, "Main menu:", reply_markup=menu)
