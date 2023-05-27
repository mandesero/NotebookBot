from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton, InlineKeyboardBuilder

from callback_data.callback_data import MenuCallbackData

# lang keyboard
lang_markup = ReplyKeyboardBuilder()
b1 = KeyboardButton(text="ru")
b2 = KeyboardButton(text="eng")
lang_markup.row(b1, b2)

# menu keyboard
menu_markup = InlineKeyboardBuilder()
menu_markup.button(text="New file", callback_data=MenuCallbackData(text='new'))
menu_markup.button(text="Change file", callback_data=MenuCallbackData(text='change'))
menu_markup.button(text="My files", callback_data=MenuCallbackData(text='my'))
