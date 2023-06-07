__all__ = ['client', 'bot_commands', 'register_user_commands']

from aiogram import Router, F
from aiogram.filters import CommandStart, Command

from handlers.client import (
    command_start, command_help,
    choose_lang, bot_commands,
    get_menu, AddingStates,
    get_new_file_name, add_new_file,
    get_new_file, create_new_notebook
)
from callback_data.callback_data import MenuCallbackData


def register_user_commands(router: Router) -> None:
    router.message.register(command_start, CommandStart())
    router.message.register(command_help, Command(commands=['help']))
    router.message.register(choose_lang, F.text == "ru")
    router.message.register(choose_lang, F.text == "eng")
    router.message.register(get_menu, F.text.lower() == 'menu')

    router.message.register(get_new_file_name, F.text == "Add new file")
    router.message.register(add_new_file, AddingStates.waiting_for_name)
    router.message.register(get_new_file, AddingStates.waiting_for_file)
    router.message.register(create_new_notebook, AddingStates.creating_notebook)



