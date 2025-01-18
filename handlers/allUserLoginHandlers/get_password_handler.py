from bot import dp,db_manager,message_store
import asyncio
import base64
from aiogram import types
from aiogram.dispatcher import FSMContext
from states import AuthStates,GetPasswordStates
from utils.password_util import decrypt_password
from utils.helpers import delete_message_after_delay
from keyboards import main_keyboard

async def get_password(message: types.Message,state: FSMContext):
    await message_store.clear_messages(state)
    await message_store.add_message(state,message)
    msg = await message.answer(
        "Введите имя сервиса.",
    )
    await message_store.add_message(state,msg)
    await GetPasswordStates.waiting_for_name.set()

@dp.message_handler(state=GetPasswordStates.waiting_for_name)
async def handle_password_name(message: types.Message, state: FSMContext):
    await message_store.add_message(state,message)
    name = message.text
    user_id = str(message.from_user.id)
    user_data = db_manager.load_user_data(user_id)
    master_password = user_data["master_password"]
    salt = base64.b64decode(user_data["salt"])

    if name not in user_data["passwords"]:
        msg1 = await message.answer("Такого пароля нет.",reply_markup=main_keyboard)
        await message_store.add_message(state,msg1)
    else:
        encrypted_password = user_data["passwords"][name]
        decrypted_password = decrypt_password(encrypted_password, master_password, salt)
        m1 = await message.answer(f"Пароль для {name}:",reply_markup=main_keyboard)
        m2 = await message.answer(f"{decrypted_password}")
        await message_store.add_message(state,m1)
        await message_store.add_message(state,m2)
        asyncio.create_task(delete_message_after_delay(m2, 10))

    await state.reset_state(with_data=False)
    await AuthStates.logged_in.set()