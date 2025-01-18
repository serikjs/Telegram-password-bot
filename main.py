from aiogram import executor
from bot import dp

import handlers.auth_handler
import handlers.all_user_login_handler

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)