from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.types.inline_keyboard import InlineKeyboardButton

# lang_kb = ReplyKeyboardMarkup(resize_keyboard=True)
# lang_kb.row(KeyboardButton("eng"), KeyboardButton("ru"))

from callback_data.callback_data import lang_callback

languare_keyboard = InlineKeyboardMarkup(
    row_width=1,
    inline_keyboard=[

        [
            InlineKeyboardButton(
                text="eng",
                callback_data=lang_callback.new("eng")
            )
        ],

        [
            InlineKeyboardButton(
                text="ru",
                callback_data="lang_kb:ru"
            )
        ]

    ]
)
