from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

add_password_keyboard = InlineKeyboardMarkup(row_width=2)
add_password_keyboard.add(
    InlineKeyboardButton(text="Ввести пароль", callback_data="enter_password"),
    InlineKeyboardButton(text="Сгенерировать пароль", callback_data="generate_password")
)