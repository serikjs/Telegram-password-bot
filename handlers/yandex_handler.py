from aiogram import types
from aiogram.dispatcher import FSMContext
import os
import base64
from aiogram.types.base import Boolean
import requests
from states import YandexDiskStates, AuthStates
from bot import dp,db_manager,message_store
from keyboards import main_keyboard
from utils.password_util import encrypt_password, decrypt_password

async def upload_to_yandex_disk(message: types.Message, token, state: FSMContext, tokenInBase: Boolean = False):
    user_id = str(message.from_user.id)

    msg1 = await message.answer("Идёт загрузка файла на Яндекс.Диск...")
    await message_store.add_message(state,msg1)

    # Проверяем наличие файла database.py
    file_path = f"database/db/{user_id}.json"
    if not os.path.exists(file_path):
        msg2 = await message.answer("Файл не найден.",reply_markup=main_keyboard)
        await message_store.add_message(state,msg2)
        return

    # Сохраняем токен в базе данных для пользователя
    if not tokenInBase :
        user_data = db_manager.load_user_data(user_id)
        master_password = user_data["master_password"]
        salt = base64.b64decode(user_data["salt"])

        encrypted_token= encrypt_password(token, master_password, salt)
        user_data["yandex_token"] = encrypted_token  # Сохраняем токен
        db_manager.save_user_data(user_id, user_data)


     # Создаем уникальную директорию для каждого пользователя на Яндекс.Диске
    user_disk_directory = f"/help_password_bot"


    headers = {
        "Authorization": f"OAuth {token}",
        "Content-Type": "application/json",
    }

      # Создаём директорию, если её не существует
    create_dir_url = "https://cloud-api.yandex.net/v1/disk/resources"
    params = {"path": user_disk_directory}
    create_dir_response = requests.put(create_dir_url, headers=headers, params=params)


    if create_dir_response.status_code != 201 and create_dir_response.status_code != 409:
        msg3 = await message.answer(
            f"Не удалось создать директорию на Яндекс.Диске. Ответ: {create_dir_response.text}",reply_markup=main_keyboard
        )
        await message_store.add_message(state,msg3)
        await state.finish()
        await AuthStates.logged_in.set()
        return

    # Сформируем путь к файлу в директории
    user_disk_file_path = f"{user_disk_directory}/{user_id}.json"


    # Запрашиваем ссылку для загрузки в личную папку пользователя
    upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    params = {"path": user_disk_file_path, "overwrite": "true"}
    response = requests.get(upload_url, headers=headers, params=params)

    if response.status_code != 200:
        msg4 = await message.answer(
            "Не удалось получить ссылку для загрузки. Проверьте токен и повторите попытку.",reply_markup=main_keyboard
        )
        await message_store.add_message(state,msg4)
        await state.finish()
        await AuthStates.logged_in.set()
        return

    href = response.json().get("href")
    if not href:
        msg5 = await message.answer("Не удалось получить ссылку для загрузки.",reply_markup=main_keyboard)
        await message_store.add_message(state,msg5)
        return

    # Загружаем файл в личную папку пользователя
    with open(file_path, "rb") as f:
        upload_response = requests.put(href, files={"file": f})

    if upload_response.status_code == 201:
        msg6 = await message.answer(f"Файл успешно загружен на Яндекс.Диск в папку /user_{user_id}!",reply_markup=main_keyboard)
        await message_store.add_message(state,msg6)
    else:
        msg7 = await message.answer("Ошибка загрузки файла на Яндекс.Диск.",reply_markup=main_keyboard)
        await message_store.add_message(state,msg7)

# Получение токена и загрузка файла на Яндекс.Диск
@dp.message_handler(state=AuthStates.logged_in, text="Синхронизировать с Яндекс.Диск")
async def request_yandex_token(message: types.Message,state: FSMContext):
    await message_store.clear_messages(state)
    await message_store.add_message(state,message)
    # Запрос на OAuth авторизацию для получения токена
    user_id = str(message.from_user.id)
    user_data = db_manager.load_user_data(user_id)

    if "yandex_token" in user_data and user_data["yandex_token"]:
        token = user_data["yandex_token"]  # Используем токен, который уже есть

        master_password = user_data["master_password"]
        salt = base64.b64decode(user_data["salt"])

        decrypted_token = decrypt_password(token, master_password, salt)
        await upload_to_yandex_disk(message, decrypted_token,state,True)
        return

    oauth_url = "https://oauth.yandex.ru/authorize?response_type=token&client_id=b4cfd561b1a2478dab705cccdd22c718"
    msg = await message.answer(
        f"Для загрузки файла на Яндекс.Диск перейдите по следующей ссылке и авторизуйтесь:\n{oauth_url}\n\n"
        "После авторизации скопируйте токен и отправьте его сюда."
    )
    await message_store.add_message(state,msg)
    await YandexDiskStates.waiting_for_token.set()

# Получение токена и загрузка файла на Яндекс.Диск
@dp.message_handler(state=YandexDiskStates.waiting_for_token)
async def handle_token(message: types.Message, state: FSMContext):
    await message_store.add_message(state,message)
    token = message.text.strip()
    await upload_to_yandex_disk(message, token, state)
    await state.finish()
    await AuthStates.logged_in.set()
