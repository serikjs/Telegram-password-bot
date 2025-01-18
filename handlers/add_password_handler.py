from aiogram import types
from aiogram.dispatcher.filters import Text
import base64
from aiogram.dispatcher import FSMContext
from states import AuthStates,AddPasswordStates
from bot import dp,db_manager, message_store, bot
from utils.password_util import encrypt_password, generate_password
from keyboards import main_keyboard,add_password_keyboard


@dp.message_handler(state=AuthStates.logged_in, text="Добавить пароль")
async def add_password(message: types.Message):
    message_store.clear_messages()
    message_store.add_message(message)
    await AddPasswordStates.waiting_for_name.set()
    msg = await message.answer("Введите имя сервиса.")
    message_store.add_message(msg)

@dp.message_handler(state=AddPasswordStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    message_store.add_message(message)
    name = message.text
    await state.update_data(name=name)
    user_id = str(message.from_user.id)
    user_data = db_manager.load_user_data(user_id)
    
    if name in user_data["passwords"]:
        msg1 = await message.answer("Пароль с таким именем уже существует.",reply_markup=main_keyboard)
        message_store.add_message(msg1)
        await state.finish()
        await AuthStates.logged_in.set()
        return
    else:
        msg2 = await message.answer("Выберите, хотите ли вы ввести пароль или сгенерировать его.", 
                             reply_markup=add_password_keyboard)
        message_store.add_message(msg2)

@dp.callback_query_handler(Text(equals="enter_password"), state=AddPasswordStates.waiting_for_name)
async def handle_enter_password(callback_query: types.CallbackQuery, state: FSMContext):
    await AddPasswordStates.waiting_for_password.set()
    msg1 = await bot.send_message(callback_query.from_user.id, "Введите пароль.")
    message_store.add_message(msg1)
    await bot.answer_callback_query(callback_query.id)  # Уведомление Telegram, что запрос обработан


@dp.callback_query_handler(Text(equals="generate_password"), state=AddPasswordStates.waiting_for_name)
async def handle_generate_password(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = str(callback_query.from_user.id)
    user_data = db_manager.load_user_data(user_id)
    master_password = user_data["master_password"]
    salt = base64.b64decode(user_data["salt"])
    generated_password = generate_password()

    name = data.get("name")

    encrypted_password = encrypt_password(generated_password, master_password, salt)
    user_data["passwords"][name] = encrypted_password
    db_manager.save_user_data(user_id, user_data)

    msg1 = await bot.send_message(callback_query.from_user.id, f"Пароль для {name} сгенерирован и сохранен.", reply_markup=main_keyboard)
    message_store.add_message(msg1)
    await state.finish()
    await AuthStates.logged_in.set()
    await bot.answer_callback_query(callback_query.id)  # Уведомление Telegram, что запрос обработан


@dp.message_handler(state=AddPasswordStates.waiting_for_password)
async def process_password(message: types.Message, state: FSMContext):
    password = message.text
    await message.delete()
    user_id = str(message.from_user.id)
    user_data = db_manager.load_user_data(user_id)
    master_password = user_data["master_password"]
    salt = base64.b64decode(user_data["salt"])

    data = await state.get_data()
    name = data.get("name")

    encrypted_password = encrypt_password(password, master_password, salt)
    user_data["passwords"][name] = encrypted_password
    db_manager.save_user_data(user_id, user_data)
    msg2 = await message.answer(f"Пароль для {name} сохранен.",reply_markup=main_keyboard)
    message_store.add_message(msg2)

    await state.finish()
    await AuthStates.logged_in.set()