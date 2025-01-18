
from aiogram.dispatcher.filters.state import State, StatesGroup
import asyncio
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

class MessagesStore(StatesGroup):
    def __init__(self):
        self.messages = []

    def add_message(self, message: str):
        self.messages.append(message)

    def get_messages(self) -> list:
        return self.messages
    
    def clear_messages(self):
        list = self.messages

        print(list)

        for msg in list:   
            asyncio.create_task(delete_message_after_delay(msg, 0))

        self.messages = []