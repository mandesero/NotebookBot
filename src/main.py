import asyncio
import logging
import os
import dotenv

from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from fluent_compiler.bundle import FluentBundle
from fluentogram import TranslatorHub, FluentTranslator, TranslatorRunner
from aiogram import Router, F
from aiogram.filters import CommandStart, Command

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

import aiohttp

from typing import Callable, Dict, Any, Awaitable, Union

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

import os
from PIL import Image
import PyPDF2
import contextlib

# ====== Config ======
dotenv.load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")


# ====================


class LocalizedTranslator:
    translator: TranslatorRunner

    def __init__(self, translator: TranslatorRunner):
        self.translator = translator

    def get(self, key: str, **kwargs) -> str:
        return self.translator.get(key, **kwargs)


class Translator:
    t_hub: TranslatorHub

    def __init__(self):
        self.t_hub = TranslatorHub(
            locales_map={
                "en": (
                    "en",
                    "ru",
                ),
                "ru": ("ru",),
            },
            translators=[
                FluentTranslator(
                    locale="en",
                    translator=FluentBundle.from_files(
                        locale="en-US",
                        filenames=[
                            "src/locales/en.ftl",
                        ],
                    ),
                ),
                FluentTranslator(
                    locale="ru",
                    translator=FluentBundle.from_files(
                        locale="ru-RU",
                        filenames=[
                            "src/locales/ru.ftl",
                        ],
                    ),
                ),
            ],
            root_locale="ru",
        )

    def get_translator(self, language: str, *args, **kwargs) -> LocalizedTranslator:
        return LocalizedTranslator(
            translator=self.t_hub.get_translator_by_locale(locale=language)
        )


usr_lang = {}


# path to file
def image_to_pdf(path: str) -> None:
    """

    :param path:
    :return:
    """
    image = Image.open(path)
    image = image.convert("RGB")
    if (idx := path.rfind("."), -5) != -1:
        path = path[:idx]
    path += ".pdf"
    image.save(path)


def make_notebook(file_name: str, usr_id: int) -> None:
    """

    :param file_name:
    :param usr_id:
    :return:
    """
    path = f"src/usr_files/{usr_id}/"
    files = [path + file for file in os.listdir(path) if file.startswith(str(usr_id))]
    for f in files:
        if not f.endswith(".pdf"):
            image_to_pdf(f)
            os.remove(f)

    pdf_files_list = [
        path + file for file in os.listdir(path) if file.startswith(str(usr_id))
    ]

    with contextlib.ExitStack() as stack:
        pdf_merger = PyPDF2.PdfMerger()
        files = [stack.enter_context(open(pdf, "rb")) for pdf in pdf_files_list]
        for f in files:
            pdf_merger.append(f)
        with open(path + file_name + ".pdf", "wb") as f:
            pdf_merger.write(f)
    for f in pdf_files_list:
        os.remove(f)


def update_notebook(file_name: str, usr_id: int) -> None:
    """

    :param file_name:
    :param usr_id:
    :return:
    """
    path = f"src/usr_files/{usr_id}/"
    files = [path + file for file in os.listdir(path) if file.startswith(str(usr_id))]
    for f in files:
        if not f.endswith(".pdf"):
            image_to_pdf(f)
            os.remove(f)

    pdf_files_list = [
        path + file for file in os.listdir(path) if file.startswith(str(usr_id))
    ] + [path + file_name + ".pdf"]

    with contextlib.ExitStack() as stack:
        pdf_merger = PyPDF2.PdfMerger()
        files = [stack.enter_context(open(pdf, "rb")) for pdf in pdf_files_list]
        for f in files:
            pdf_merger.append(f)
        with open(path + file_name + ".pdf", "wb") as f:
            pdf_merger.write(f)
    for f in pdf_files_list:
        if f != path + file_name + ".pdf":
            os.remove(f)


class Simple_Middleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any],
    ) -> Any:
        return await handler(event, data)


async def download_file(url: str, destination_path: str, file_name: str) -> None:
    """
    Скачивание пользовательских файлов
    :param url: (str)
    :param destination_path: (str)
    :param file_name:  (str)
    :return:
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
            with open(f"{destination_path}/{file_name}", "wb") as f:
                f.write(data)


bot_commands = {
    (
        "start",
        "start messaging with bot",
    ),
    (
        "help",
        "get some help",
    ),
    (
        "menu",
        "return menu",
    ),
}


class AddingStates(StatesGroup):
    """
    Adding states
    """

    waiting_for_name = State()
    waiting_for_file = State()
    creating_notebook = State()


class ShowingStates(StatesGroup):
    """
    ShowingStates
    """

    waiting_for_choose = State()


class ChangingStates(StatesGroup):
    """
    ChangingStates
    """

    waiting_for_name = State()
    waiting_for_adding = State()
    updating_notebook = State()


async def command_start(message: types.Message) -> types.Message:
    """
    Начало работы с ботом. Выбор локали

    :param message: command "/start"
    :return: None
    """
    user_id = message.from_user.id
    if "usr_files" not in os.listdir("."):
        os.mkdir("usr_files")

    if str(user_id) not in os.listdir("src/usr_files/"):
        os.mkdir(f"src/usr_files/{user_id}")
    usr_lang[user_id] = "en"

    lang_markup = ReplyKeyboardBuilder()
    lang_markup.button(text="ru", callback_data="ru")
    lang_markup.button(text="en", callback_data="en")
    lang_markup.adjust(2)

    return await message.answer(
        text="Hello",
        reply_markup=lang_markup.as_markup(
            resize_keyboard=True, one_time_keyboard=True
        ),
    )


async def command_help(message: types.Message, command: CommandObject) -> types.Message:
    """
    Получение справки по доступным командам

    :param message: command "/help"
    :return: description of the command
    """
    for cmd in bot_commands:
        if cmd[0] == command.args:
            return await message.answer(text=f"{cmd[0]} - {cmd[1]}")

    return await message.answer(
        text=f"Command {command.args} not found. \n\n use /help <command>"
    )


async def choose_lang(message: types.Message, translator: Translator) -> None:
    """
    Установка локали

    :param message: languages ["ru" | "eng"]
    :return: None
    """
    trans = translator.get_translator(language=message.text.lower())
    t = trans.get("test")
    usr_lang[message.from_user.id] = message.text.lower()
    await message.answer(text=f"{t} + You choose {message.text}")


async def get_menu(message: types.Message) -> None:
    menu_markup = ReplyKeyboardBuilder()
    menu_markup.button(text="Add new file", callback_data="add_new_file")
    menu_markup.button(text="Change file", callback_data="change_file")
    menu_markup.button(text="Show my notebooks", callback_data="show_notebooks")
    menu_markup.adjust(1)
    await message.answer(
        text="Menu",
        reply_markup=menu_markup.as_markup(
            resize_keyboard=True, one_time_keyboard=True
        ),
    )


async def get_new_file_name(message: types.Message, state: FSMContext) -> None:
    """

    :param message:
    :param state:
    :return:
    """
    await state.set_state(AddingStates.waiting_for_name)

    cancel_board = ReplyKeyboardBuilder()
    cancel_board.button(text="Cancel")

    await message.answer(
        text="Enter name of the notebook",
        reply_markup=cancel_board.as_markup(
            resize_keyboard=True, one_time_keyboard=True
        ),
    )


async def add_new_file(
    message: types.Message, state: FSMContext, translator: Translator
) -> None:
    """

    :param message:
    :param state:
    :param translator:
    :return:
    """
    if message.text == "Cancel":
        await state.clear()
        return

    await state.update_data(name=message.text)
    await state.set_state(AddingStates.waiting_for_file)

    cancel_board = ReplyKeyboardBuilder()
    cancel_board.button(text="Cancel")
    trans = translator.get_translator(language=usr_lang[message.from_user.id])
    await message.answer(
        text=trans.get("upload"),
        reply_markup=cancel_board.as_markup(
            resize_keyboard=True, one_time_keyboard=True
        ),
    )


async def get_new_file(message: types.Message, state: FSMContext):
    """

    :param message:
    :param state:
    :return:
    """
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
    url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    await download_file(
        url=url,
        destination_path=f"src/usr_files/{message.from_user.id}",
        file_name=file_name,
    )


async def create_new_notebook(message: types.Message, state: FSMContext) -> None:
    """

    :param message:
    :param state:
    :return:
    """
    data = await state.get_data()
    print(data)
    await message.answer(text=f"Making {data['name']}...")

    make_notebook(f'{data["name"]}', message.from_user.id)
    await state.clear()
    await message.answer(text=f"{data['name']} complete")


# ========================== Show user files ==========================


async def show_user_notebooks(
    message: types.Message, state: FSMContext, translator: Translator
) -> None:
    """

    :param message:
    :param state:
    :param translator:
    :return:
    """
    usr_id = message.from_user.id
    files = [
        file
        for file in os.listdir(f"src/usr_files/{usr_id}/")
        if not file.startswith(str(usr_id))
    ]
    if not files:
        await state.clear()
        return
    await state.set_state(ShowingStates.waiting_for_choose)
    notebooks_markup = InlineKeyboardBuilder()
    for file in files:
        file_name = file.split(".")[0]
        notebooks_markup.button(text=file_name, callback_data=f"{file_name}")
    notebooks_markup.adjust(1)
    trans = translator.get_translator(language=usr_lang[message.from_user.id])
    await message.answer(
        text=trans.get("yournotebooks"),
        reply_markup=notebooks_markup.as_markup(
            resize_keyboard=True, one_time_keyboard=True
        ),
    )


async def send_notebook(callback: types.CallbackQuery, state: FSMContext) -> None:
    """

    :param callback:
    :param state:
    :return:
    """
    await state.clear()
    files = os.listdir(f"src/usr_files/{callback.from_user.id}/")
    for file in files:
        if file.startswith(callback.data):
            file_obj = FSInputFile(f"src/usr_files/{callback.from_user.id}/{file}")
            await SendDocument(chat_id=callback.message.chat.id, document=file_obj)
            break


# ========================== Changing user files ==========================


async def changing_user_notebook(
    message: types.Message, state: FSMContext, translator: Translator
) -> None:
    """

    :param message:
    :param state:
    :param translator:
    :return:
    """
    await state.set_state(ChangingStates.waiting_for_name)
    usr_id = message.from_user.id
    files = [
        file
        for file in os.listdir(f"src/usr_files/{usr_id}/")
        if not file.startswith(str(usr_id))
    ]
    if not files:
        await state.clear()
        return
    notebooks_markup = ReplyKeyboardBuilder()
    for file in files:
        file_name = file.split(".")[0]
        notebooks_markup.button(text=file_name, callback_data=f"file_{file_name}")
    notebooks_markup.adjust(1)
    trans = translator.get_translator(language=usr_lang[message.from_user.id])
    await message.answer(
        text=trans.get("choose"),
        reply_markup=notebooks_markup.as_markup(
            resize_keyboard=True, one_time_keyboard=True
        ),
    )


async def get_change_to_notebook(
    message: types.Message, state: FSMContext, translator: Translator
) -> None:
    """

    :param message:
    :param state:
    :param translator:
    :return:
    """
    await state.update_data(name=message.text)
    await state.set_state(ChangingStates.waiting_for_adding)

    cancel_board = ReplyKeyboardBuilder()
    cancel_board.button(text="Cancel")
    trans = translator.get_translator(language=usr_lang[message.from_user.id])
    await message.answer(
        text=trans.get("upload"),
        reply_markup=cancel_board.as_markup(
            resize_keyboard=True, one_time_keyboard=True
        ),
    )


async def get_files_to_update(message: types.Message, state: FSMContext) -> None:
    """

    :param message:
    :param state:
    :return:
    """
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
    url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    await download_file(
        url=url,
        destination_path=f"src/usr_files/{message.from_user.id}",
        file_name=file_name,
    )


async def make_changes(message: types.Message, state: FSMContext) -> None:
    """

    :param message:
    :param state:
    :return:
    """
    data = await state.get_data()

    await message.answer(text=f"Starting adding to {data['name']}")

    update_notebook(f'{data["name"]}', message.from_user.id)


def register_user_commands(router: Router) -> None:
    router.message.register(command_start, CommandStart())
    router.message.register(command_help, Command(commands=["help"]))
    router.message.register(choose_lang, F.text == "en")
    router.message.register(choose_lang, F.text == "ru")
    router.message.register(get_menu, F.text.lower() == "menu")

    router.message.register(get_new_file_name, F.text == "Add new file")
    router.message.register(add_new_file, AddingStates.waiting_for_name)
    router.message.register(get_new_file, AddingStates.waiting_for_file)
    router.message.register(create_new_notebook, AddingStates.creating_notebook)

    router.message.register(show_user_notebooks, F.text == "Show my notebooks")
    router.callback_query.register(send_notebook, ShowingStates.waiting_for_choose)

    router.message.register(changing_user_notebook, F.text == "Change file")
    router.message.register(get_change_to_notebook, ChangingStates.waiting_for_name)
    router.message.register(get_files_to_update, ChangingStates.waiting_for_adding)
    router.message.register(make_changes, ChangingStates.updating_notebook)

    router.message.register(Simple_Middleware)
    router.callback_query.register(Simple_Middleware)


async def main():
    logging.basicConfig(level=logging.DEBUG)

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    bot = Bot(token=BOT_TOKEN)

    register_user_commands(dp)

    await bot.set_my_commands(
        commands=[
            BotCommand(command=cmd[0], description=cmd[1]) for cmd in bot_commands
        ]
    )

    await dp.start_polling(bot, translator=Translator())


def run_bot():
    asyncio.run(main())


if __name__ == "__main__":
    run_bot()
