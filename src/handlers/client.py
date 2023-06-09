import asyncio

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.methods import SendDocument
from aiogram.methods.get_file import GetFile
from aiogram.filters import CommandObject
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from time import time
import os
from scripts.convert import make_notebook

from config import BOT_TOKEN

import aiohttp

from locale.translator import LocalizedTranslator, Translator

usr_lang = {}


async def download_file(url: str, destination_path: str, file_name: str) -> None:
    '''
    Скачивание пользовательских файлов
    :param url: (str)
    :param destination_path: (str)
    :param file_name:  (str)
    :return:
    '''
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
            with open(f"{destination_path}/{file_name}", "wb") as f:
                f.write(data)


bot_commands = {
    ("start", "start messaging with bot",),
    ("help", "get some help",),
    ("menu", "return menu",)
}


class AddingStates(StatesGroup):
    '''
        Adding states
    '''
    waiting_for_name = State()
    waiting_for_file = State()
    creating_notebook = State()


class ShowingStates(StatesGroup):
    '''
        ShowingStates
    '''
    waiting_for_choose = State()


class ChangingStates(StatesGroup):
    '''
        ChangingStates
    '''
    waiting_for_name = State()
    waiting_for_adding = State()
    updating_notebook = State()


async def command_start(message: types.Message) -> None:
    """
    Начало работы с ботом. Выбор локали

    :param message: command "/start"
    :return: None
    """
    user_id = message.from_user.id
    if str(user_id) not in os.listdir("../usr_files/"):
        os.mkdir(f"../usr_files/{user_id}")
    usr_lang[user_id] = 'en'

    lang_markup = ReplyKeyboardBuilder()
    lang_markup.button(text="ru", callback_data="ru")
    lang_markup.button(text="en", callback_data="en")
    lang_markup.adjust(2)

    await message.answer(
        "Hello",
        reply_markup=lang_markup.as_markup(
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


async def command_help(message: types.Message, command: CommandObject) -> types.Message:
    """
    Получение справки по доступным командам

    :param message: command "/help"
    :return: description of the command
    """
    for cmd in bot_commands:
        if cmd[0] == command.args:
            return await message.answer(
                text=f"{cmd[0]} - {cmd[1]}"
            )

    return await message.answer(
        text=f"Command {command.args} not found. \n\n use /help <command>"
    )


async def choose_lang(message: types.Message, translator: Translator) -> None:
    """
    Установка локали

    :param message: locale ["ru" | "eng"]
    :return: None
    """
    trans = translator.get_translator(language=message.text.lower())
    t = trans.get('test')
    usr_lang[message.from_user.id] = message.text.lower()
    await message.answer(text=f"{t} + You choose {message.text}")


async def get_menu(message: types.Message) -> None:
    menu_markup = ReplyKeyboardBuilder()
    menu_markup.button(text="Add new file", callback_data="add_new_file")
    menu_markup.button(text="Change file", callback_data="change_file")
    menu_markup.button(text="Show my notebooks", callback_data="show_notebooks")
    menu_markup.adjust(1)
    await message.answer(
        text='Menu',
        reply_markup=menu_markup.as_markup(
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


async def get_new_file_name(message: types.Message, state: FSMContext) -> None:
    '''

    :param message:
    :param state:
    :return:
    '''
    await state.set_state(AddingStates.waiting_for_name)

    cancel_board = ReplyKeyboardBuilder()
    cancel_board.button(text="Cancel")

    await message.answer(
        text="Enter name of the notebook",
        reply_markup=cancel_board.as_markup(
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


async def add_new_file(message: types.Message, state: FSMContext, translator: Translator) -> None:
    '''

    :param message:
    :param state:
    :param translator:
    :return:
    '''
    if message.text == "Cancel":
        await state.clear()
        return

    await state.update_data(name=message.text)
    await state.set_state(AddingStates.waiting_for_file)

    cancel_board = ReplyKeyboardBuilder()
    cancel_board.button(text="Cancel")
    trans = translator.get_translator(language=usr_lang[message.from_user.id])
    await message.answer(
        text=trans.get('upload'),
        reply_markup=cancel_board.as_markup(
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


async def get_new_file(message: types.Message, state: FSMContext):
    '''

    :param message:
    :param state:
    :return:
    '''
    if message.text and message.text == "Cancel":
        await state.clear()
        return

    if message.text:
        await state.set_state(AddingStates.creating_notebook)
        await message.answer(text="Waiting...")
        await asyncio.sleep(20)
        return await create_new_notebook(message, state)

    if message.document:
        file_id = message.document.file_id
        file_name = f"{message.from_user.id}_{int(time() * 1e8)}.pdf"

    if message.photo:
        file_id = message.photo[-1].file_id
        file_name = f"{message.from_user.id}_{int(time() * 1e8)}.jpeg"

    file_info = await GetFile(file_id=file_id)
    file_path = file_info.file_path
    url = f'https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}'
    await download_file(url=url, destination_path=f'../usr_files/{message.from_user.id}', file_name=file_name)


async def create_new_notebook(message: types.Message, state: FSMContext) -> None:
    '''

    :param message:
    :param state:
    :return:
    '''
    data = await state.get_data()
    print(data)
    await message.answer(
        text=f"Making {data['name']}..."
    )

    make_notebook(f'{data["name"]}', message.from_user.id)
    await state.clear()
    await message.answer(text=f"{data['name']} complete")


# ========================== Show user files ==========================

async def show_user_notebooks(message: types.Message, state: FSMContext, translator: Translator) -> None:
    '''

    :param message:
    :param state:
    :param translator:
    :return:
    '''
    usr_id = message.from_user.id
    files = [file for file in os.listdir(f'../usr_files/{usr_id}/') if not file.startswith(str(usr_id))]
    if not files:
        await state.clear()
        return
    await state.set_state(ShowingStates.waiting_for_choose)
    notebooks_markup = InlineKeyboardBuilder()
    for file in files:
        file_name = file.split('.')[0]
        notebooks_markup.button(text=file_name, callback_data=f"{file_name}")
    notebooks_markup.adjust(1)
    trans = translator.get_translator(language=usr_lang[message.from_user.id])
    await message.answer(
        text=trans.get('yournotebooks'),
        reply_markup=notebooks_markup.as_markup(
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


async def send_notebook(callback: types.CallbackQuery, state: FSMContext) -> None:
    '''

    :param callback:
    :param state:
    :return:
    '''
    await state.clear()
    files = os.listdir(f'../usr_files/{callback.from_user.id}/')
    for file in files:
        if file.startswith(callback.data):
            file_obj = FSInputFile(f'../usr_files/{callback.from_user.id}/{file}')
            await SendDocument(chat_id=callback.message.chat.id, document=file_obj)
            break


# ========================== Changing user files ==========================

async def changing_user_notebook(message: types.Message, state: FSMContext, translator: Translator) -> None:
    '''

    :param message:
    :param state:
    :param translator:
    :return:
    '''
    await state.set_state(ChangingStates.waiting_for_name)
    usr_id = message.from_user.id
    files = [file for file in os.listdir(f'../usr_files/{usr_id}/') if not file.startswith(str(usr_id))]
    if not files:
        await state.clear()
        return
    notebooks_markup = ReplyKeyboardBuilder()
    for file in files:
        file_name = file.split('.')[0]
        notebooks_markup.button(text=file_name, callback_data=f"file_{file_name}")
    notebooks_markup.adjust(1)
    trans = translator.get_translator(language=usr_lang[message.from_user.id])
    await message.answer(
        text=trans.get('choose'),
        reply_markup=notebooks_markup.as_markup(
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


async def get_change_to_notebook(message: types.Message, state: FSMContext, translator: Translator) -> None:
    '''

    :param message:
    :param state:
    :param translator:
    :return:
    '''
    await state.update_data(name=message.text)
    await state.set_state(ChangingStates.waiting_for_adding)

    cancel_board = ReplyKeyboardBuilder()
    cancel_board.button(text="Cancel")
    trans = translator.get_translator(language=usr_lang[message.from_user.id])
    await message.answer(
        text=trans.get('upload'),
        reply_markup=cancel_board.as_markup(
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


async def get_files_to_update(message: types.Message, state: FSMContext) -> None:
    '''

    :param message:
    :param state:
    :return:
    '''
    if message.text and message.text == "Cancel":
        await state.clear()
        return

    if message.text and message.text.lower() == "done":
        await state.set_state(ChangingStates.updating_notebook)
        await message.answer(text="Waiting...")
        await asyncio.sleep(20)
        return await make_changes(message, state)

    if message.document:
        file_id = message.document.file_id
        file_name = f"{message.from_user.id}_{int(time() * 1e8)}.pdf"

    if message.photo:
        file_id = message.photo[-1].file_id
        file_name = f"{message.from_user.id}_{int(time() * 1e8)}.jpeg"

    file_info = await GetFile(file_id=file_id)
    file_path = file_info.file_path
    url = f'https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}'
    await download_file(url=url, destination_path=f'../usr_files/{message.from_user.id}', file_name=file_name)


async def make_changes(message: types.Message, state: FSMContext) -> None:
    '''

    :param message:
    :param state:
    :return:
    '''
    data = await state.get_data()

    await message.answer(text=f"Starting adding to {data['name']}")

    # make_notebook(f'{data["name"]}.pdf', message.from_user.id)
