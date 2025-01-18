from cgitb import text
from bot import dp,db_manager,message_store
from aiogram import types
import os
import base64
from aiogram.dispatcher import FSMContext
from states import AuthStates
from utils.password_util import hash_password, verify_password
from keyboards import clear_keyboard, main_keyboard, auth_keyboard

@dp.message_handler(commands=["start"])
async def start(message: types.Message, state: FSMContext):
    await send_welcome(message,state)

@dp.message_handler(text="Войти")
async def start(message: types.Message, state: FSMContext):
    await send_welcome(message,state)


async def send_welcome(message: types.Message, state: FSMContext):
    await message.delete()
    msg = await message.answer(
        "Добро пожаловать! Введите мастер-пароль для авторизации или регистрации.",
        reply_markup=clear_keyboard
    )
    await message_store.add_message(state,msg)
    await AuthStates.waiting_for_master_password.set()

@dp.message_handler(state=AuthStates.waiting_for_master_password)
async def handle_master_password(message: types.Message, state: FSMContext):
    await message.delete()
    master_password = message.text
    user_id = str(message.from_user.id)

    # Регистрация нового пользователя
    hash_password(master_password)  # Хэширование пароля для примера

    if db_manager.user_exists(user_id):
        # Загружаем данные пользователя
        user_data = db_manager.load_user_data(user_id)
        saved_password_hash = user_data["master_password"]

        # Проверяем совпадение паролей
        if verify_password(master_password, saved_password_hash):
            await AuthStates.logged_in.set()
            msg1 =await message.answer(
                "Авторизация успешна! Вы вошли в аккаунт.", 
                reply_markup=main_keyboard
            )
            await message_store.add_message(state,msg1)
        else:
            msg2 = await message.answer("Неверный мастер-пароль. Попробуйте снова.")
            await message_store.add_message(state,msg2)
    else:
        salt = os.urandom(16)
        
        # Регистрация нового пользователя
        user_data = {
            "user_id": user_id,
            "master_password": hash_password(master_password),
            "salt": base64.b64encode(salt).decode(),
            "passwords": {},
        }
        db_manager.save_user_data(user_id, user_data)
        await AuthStates.logged_in.set()
        msg3 = await message.answer(
            "Регистрация завершена! Вы авторизованы.", 
            reply_markup=main_keyboard
        )
        await message_store.add_message(state,msg3)

@dp.message_handler(state=AuthStates.logged_in, text="Выйти")
async def logout(message: types.Message, state: FSMContext):
    await message.delete()
    await message_store.clear_messages(state)
    await state.finish()
    await message.answer("Вы вышли из аккаунта.",reply_markup=auth_keyboard)
