__all__ = ['client', 'bot_commands', 'register_user_commands']

from aiogram import Router, F
from aiogram.filters import CommandStart, Command

from handlers.client import command_start, command_help, choose_lang, bot_commands, get_menu, menu_callback_filter
from callback_data.callback_data import MenuCallbackData


def register_user_commands(router: Router) -> None:
    router.message.register(command_start, CommandStart())
    router.message.register(command_help, Command(commands=['help']))
    router.message.register(choose_lang, F.text == "ru")
    router.message.register(choose_lang, F.text == "eng")
    router.message.register(get_menu, F.text == 'menu')
    router.callback_query.register(menu_callback_filter, MenuCallbackData.filter())
