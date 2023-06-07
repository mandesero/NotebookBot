from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.methods.get_file import GetFile
from aiogram.filters import CommandObject
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from time import time

from config import BOT_TOKEN

from keyboards.client_kb import lang_markup, menu_markup
from callback_data.callback_data import MenuCallbackData
import aiohttp


async def download_file(url, destination_path, file_name):
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


async def command_start(message: types.Message) -> None:
    """
    Start messaging with bot. Ability to set locale.

    :param message: command "/start"
    :return: None
    """
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
    menu_markup.button(text="Show my files", callback_data="show_files")
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
    # await state.set_data({"name", message.text})
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
    if message.text == "Cancel":
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
    await download_file(url=url, destination_path='../downloads/', file_name=file_name)


async def create_new_notebook(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    print(data)
    await message.answer(
        text=f"New - {data['name']}"
    )
