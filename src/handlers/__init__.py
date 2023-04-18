__all__ = ['client', 'bot_commands']

from aiogram import Router, F
from aiogram.filters import CommandStart, Command

from handlers.client import command_start, command_help, choose_lang

bot_commands = {
    ("start", "начать общение с ботом", ),
    ("help", "помощь", )
}

def register_user_commands(router: Router):
    router.message.register(command_start, CommandStart())
    router.message.register(command_help, Command(commands=['help']))
    router.message.register(choose_lang, F.text == "ru")
    router.message.register(choose_lang, F.text == "eng")