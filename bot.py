import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import config
from database.database import DatabaseManager
from states import MessagesStore
logging.basicConfig(level=logging.INFO)

main_config = config
bot = Bot(token=main_config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Инициализация базы данных
db_manager = DatabaseManager()

message_store = MessagesStore()