from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton

lang_kb = ReplyKeyboardBuilder()
b1 = KeyboardButton(text="ru")
b2 = KeyboardButton(text="eng")
lang_kb.row(b1, b2)

