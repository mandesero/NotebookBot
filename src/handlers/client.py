from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot import dp, bot
from keyboards import languare_keyboard
from callback_data import lang_callback

import os
import gettext

popath = os.path.join(os.path.dirname(__file__), "po")
print(popath)
translation = gettext.translation("server", popath, languages=['en'], fallback=True)
translation_ru = gettext.translation("server", popath, languages=['ru'], fallback=True)

commands = {
    "/start": "начать общение с ботом",
    "/help": "помощь",
    "/info": "информация"
}


# class FSM_Lang(StatesGroup):
#     req = State()
#     res = State()


async def command_start(message: types.Message):
    await message.answer(
        text="Choose your languare",
        reply_markup=languare_keyboard
    )


async def set_user_lang(call: types.CallbackQuery, callback_data: dict):
    await call.answer(cache_time=5)
    if callback_data['lang'] == "ru":
        translation_ru.install()
        print("RU")
        # await call.message.answer(text='Выбран русский язык')
    elif callback_data['lang'] == "eng":
        translation.install()
        print("ENG")
        # await call.message.answer(text='English was choosen')
    await call.message.answer(text=_('English was choosen'))

async def command_help(message: types.Message):
    await bot.delete_message(
        chat_id=message.chat.id,
        message_id=message.message_id
    )
    await message.answer(
        text="Здесь пока ничего нет"
    )


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=["start"])
    dp.register_message_handler(command_help, commands=["help"])

    dp.register_callback_query_handler(set_user_lang, lang_callback.filter(), state=None)
    # dp.register_callback_query_handler(set_user_languare_eng, lang_callback.filter(lang="eng"), state=None)
