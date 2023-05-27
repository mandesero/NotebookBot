__all__ = ['client', 'bot_commands', 'register_user_commands']

from aiogram import Router, F
from aiogram.filters import CommandStart, Command

from handlers.client import command_start, command_help, choose_lang, bot_commands


def register_user_commands(router: Router) -> None:
    router.message.register(command_start, CommandStart())
    router.message.register(command_help, Command(commands=['help']))
    router.message.register(choose_lang, F.text == "ru")
    router.message.register(choose_lang, F.text == "eng")
