
from aiogram.dispatcher.filters.state import State, StatesGroup
import asyncio
from utils.helpers import delete_message_after_delay
from aiogram.dispatcher import FSMContext

class AuthStates(StatesGroup):
    waiting_for_master_password = State()
    logged_in = State()

class AddPasswordStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_password = State()

class GetPasswordStates(StatesGroup):
    waiting_for_name = State()

class YandexDiskStates(StatesGroup):
    waiting_for_token = State()

class MessagesStore:
    @staticmethod
    async def add_message(state: FSMContext, message):
        # Загружаем текущие данные пользователя
        data = await state.get_data()
        messages = data.get("messages", [])
        
        # Добавляем сообщение в список
        messages.append(message)
        
        # Сохраняем обновленный список сообщений
        await state.update_data(messages=messages)

    @staticmethod
    async def get_messages(state: FSMContext):
        # Получаем список сообщений из состояния
        data = await state.get_data()
        return data.get("messages", [])

    @staticmethod
    async def clear_messages(state: FSMContext):
        # Получаем список сообщений
        data = await state.get_data()
        messages = data.get("messages", [])

        # Удаляем сообщения
        for msg in messages:
            await msg.delete()

        # Очищаем список сообщений
        await state.update_data(messages=[])