from bot import dp,db_manager,message_store
from aiogram import types
from states import AuthStates
from aiogram.dispatcher import FSMContext
from keyboards import main_keyboard

@dp.message_handler(state=AuthStates.logged_in, text="Список паролей")
async def list_passwords(message: types.Message, state: FSMContext):
    await message_store.clear_messages(state)
    await message_store.add_message(state,message)
    user_id = str(message.from_user.id)
    user_data = db_manager.load_user_data(user_id)

    if not user_data["passwords"]:
        msg1 = await message.answer("Сохраненных паролей нет.",reply_markup=main_keyboard)
        await message_store.add_message(state,msg1)
        return

    response = "Ваши пароли:\n" + "\n".join(user_data["passwords"].keys())
    msg2 = await message.answer(response,reply_markup=main_keyboard)
    await message_store.add_message(state,msg2)