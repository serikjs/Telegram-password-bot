from bot import dp, main_config
from aiogram import types
from aiogram.dispatcher import FSMContext

from states import AuthStates,InactivityTimerStore,GetPasswordStates,AddPasswordStates,YandexDiskStates

from handlers.allUserLoginHandlers import add_password,get_password,list_passwords,request_yandex_token

@dp.message_handler(state=[AuthStates.logged_in,GetPasswordStates.waiting_for_name,AddPasswordStates.waiting_for_name,AddPasswordStates.waiting_for_password,YandexDiskStates.waiting_for_token])
async def handle_any_message(message: types.Message, state: FSMContext):
    await InactivityTimerStore.reset_inactivity_timer(state, message, main_config.TIME_TO_LOGOUT)

    if message.text == "Получить пароль":
        await get_password(message,state)
        return

    if message.text == "Добавить пароль":
        await add_password(message,state)
        return

    if message.text == "Список паролей":
        await list_passwords(message,state)
        return

    if message.text == "Синхронизировать с Яндекс.Диск":
        await request_yandex_token(message,state)
        return
