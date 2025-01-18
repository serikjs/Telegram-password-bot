from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

auth_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
auth_keyboard.add(
    KeyboardButton(text="Войти"),
)
