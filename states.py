
from aiogram.dispatcher.filters.state import State, StatesGroup
import asyncio
from aiogram import types
from aiogram.dispatcher import FSMContext

from utils.helpers import delete_message_after_delay

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
        messages = data.get("messages")
        
        if not messages:
            messages = []

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
        messages = data.get("messages")

        # Удаляем сообщения
        for msg in messages:
            await delete_message_after_delay(msg, 0)

        # Очищаем список сообщений
        await state.update_data(messages=[])

class InactivityTimerStore:
    @staticmethod
    async def start_inactivity_timer(state: FSMContext,  message: types.Message, timeout: int):
        # Сохраняем таймер (информацию о времени ожидания) в состоянии
        await state.update_data(inactivity_timer_timeout=timeout,inactivity_timer_message=message)

        # Создаем задачу для ожидания и выполнения действия
        new_timer = asyncio.create_task(InactivityTimerStore._wait_and_execute(state,message, timeout))

        # Сохраняем только информацию о задаче, не саму задачу
        await state.update_data(inactivity_timer_task_id=id(new_timer))  # Сохраняем ID задачи для отслеживания

    @staticmethod
    async def _wait_and_execute(state: FSMContext,message: types.Message, timeout: int):
        # Ожидаем время и выполняем действие
        await asyncio.sleep(timeout)
        
        # Ваше действие по истечении времени
        # Например, выход из состояния:
        data = await state.get_data()
        logout_callback = data.get("logout_callback")

        if logout_callback:
            # Выполняем callback, который содержит вашу логику logout
            await logout_callback(message, state)

        await InactivityTimerStore.cancel_inactivity_timer(state)
        await state.finish()

    @staticmethod
    async def reset_inactivity_timer(state: FSMContext,message: types.Message, timeout: int):
        await InactivityTimerStore.cancel_inactivity_timer(state)
        await InactivityTimerStore.start_inactivity_timer(state, message, timeout)

    @staticmethod
    async def cancel_inactivity_timer(state: FSMContext):
        # Получаем информацию о таймере
        data = await state.get_data()
        task_id = data.get("inactivity_timer_task_id")

        if task_id:
            # Можно отслеживать задачу по ID, например, отменить, если она еще не завершена
            task = asyncio.all_tasks()
            for t in task:
                if id(t) == task_id and not t.done():
                    t.cancel()
                    break

            # Очищаем информацию о таймере
            await state.update_data(inactivity_timer_task_id=None, inactivity_timer_timeout=None)