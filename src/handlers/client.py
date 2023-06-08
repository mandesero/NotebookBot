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

from config import BOT_TOKEN

from keyboards.client_kb import lang_markup, menu_markup
import aiohttp


async def download_file(url: str, destination_path: str, file_name: str) -> None:
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
    waiting_for_choose = State()


class ChangingStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_adding = State()
    updating_notebook = State()


async def command_start(message: types.Message) -> None:
    """
    Start messaging with bot. Ability to set locale.

    :param message: command "/start"
    :return: None
    """
    user_id = message.from_user.id
    if str(user_id) not in os.listdir("../usr_files/"):
        os.mkdir(f"../usr_files/{user_id}")

    await message.answer(
        "Hello",
        reply_markup=lang_markup.as_markup(
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


async def command_help(message: types.Message, command: CommandObject) -> types.Message:
    """
    Command for get some help.

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


async def choose_lang(message: types.Message) -> None:
    """
    Set up user locale.

    :param message: locale ["ru" | "eng"]
    :return: None
    """
    await message.answer(text=f"You choose {message.text}")


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


async def add_new_file(message: types.Message, state: FSMContext) -> None:
    if message.text == "Cancel":
        await state.clear()
        return

    await state.update_data(name=message.text)
    await state.set_state(AddingStates.waiting_for_file)

    cancel_board = ReplyKeyboardBuilder()
    cancel_board.button(text="Cancel")

    await message.answer(
        "Upload your files (Write 'done' in the end)",
        reply_markup=cancel_board.as_markup(
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


async def get_new_file(message: types.Message, state: FSMContext):
    if message.text and message.text == "Cancel":
        await state.clear()
        return

    if message.text:
        await state.set_state(AddingStates.creating_notebook)
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
    data = await state.get_data()
    print(data)
    await message.answer(
        text=f"Making {data['name']}..."
    )

    # Объединение всех файлов в data['name'].pdf, очистка мусора


# ========================== Show user files ==========================

async def show_user_notebooks(message: types.Message, state: FSMContext) -> None:
    usr_id = message.from_user.id
    files = [file for file in os.listdir(f'../usr_files/{usr_id}/') if not file.startswith(str(usr_id))]
    if not files:
        await state.clear()
        return
    await state.set_state(ShowingStates.waiting_for_choose)
    notebooks_markup = ReplyKeyboardBuilder()
    for file in files:
        file_name = file.split('.')[0]
        notebooks_markup.button(text=file_name, callback_data=f"file_{file_name}")
    notebooks_markup.adjust(1)
    await message.answer(
        text='Your notebooks:',
        reply_markup=notebooks_markup.as_markup(
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


async def send_notebook(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    files = os.listdir(f'../usr_files/{message.from_user.id}/')
    for file in files:
        if file.startswith(message.text):
            file_obj = FSInputFile(f'../usr_files/{message.from_user.id}/{file}')
            await SendDocument(chat_id=message.chat.id, document=file_obj)


# ========================== Changing user files ==========================

async def changing_user_notebook(message: types.Message, state: FSMContext) -> None:
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
    await message.answer(
        text='Choose notebook which you want to change:',
        reply_markup=notebooks_markup.as_markup(
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


async def get_change_to_notebook(message: types.Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(ChangingStates.waiting_for_adding)

    cancel_board = ReplyKeyboardBuilder()
    cancel_board.button(text="Cancel")

    await message.answer(
        text="Upload your files (Write 'done' in the end)",
        reply_markup=cancel_board.as_markup(
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


async def get_files_to_update(message: types.Message, state: FSMContext) -> None:
    if message.text and message.text == "Cancel":
        await state.clear()
        return

    if message.text and message.text.lower() == "done":
        await state.set_state(ChangingStates.updating_notebook)
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
    data = await state.get_data()
    await message.answer(text=f"Starting adding to {data['name']}")

    # Добавление всех файлов в data['name'].pdf, очистка мусора
