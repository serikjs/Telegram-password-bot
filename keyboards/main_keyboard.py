from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.add(
    KeyboardButton(text="Добавить пароль"),
    KeyboardButton(text="Получить пароль"),
    KeyboardButton(text="Список паролей"),
)
main_keyboard.add(
    KeyboardButton(text="Синхронизировать с Яндекс.Диск"),
)
main_keyboard.add(
    KeyboardButton(text="Выйти"),
)