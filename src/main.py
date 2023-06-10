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
        """
        The __init__ function is called when the class is instantiated.
        It sets up the instance of the class, and it's where you define your attributes.

        :param self: Used to Represent the instance of the class.
        :param translator:TranslatorRunner: Used to Pass the translator object to the class.
        :return: The translator.

        """
        self.translator = translator

    def get(self, key: str, **kwargs) -> str:
        """
        The get function is a wrapper around the gettext.gettext function,
        which is used to translate strings into the current locale.

        :param self: Used to Represent the instance of the class.
        :param key:str: Used to Specify the key of the dictionary.
        :param **kwargs: Used to Pass a variable number of keyword arguments to the function.
        :return: A string.

        """
        return self.translator.get(key, **kwargs)


class Translator:
    t_hub: TranslatorHub

    def __init__(self):
        """
        The __init__ function is called when the class is instantiated.
        It sets up the TranslatorHub object, which will be used to translate strings.
        The locales_map parameter specifies which languages are available for each locale.
        In this case, we have two locales: "en" and "ru". The root locale is set to "ru", so it will be used as a fallback if no other translation can be found.

        :param self: Used to Represent the instance of the class.
        :return: An instance of the translatorhub class.

        """
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
                            f"{__file__[:-8]}/en.ftl",
                        ],
                    ),
                ),
                FluentTranslator(
                    locale="ru",
                    translator=FluentBundle.from_files(
                        locale="ru-RU",
                        filenames=[
                            f"{__file__[:-8]}/ru.ftl",
                        ],
                    ),
                ),
            ],
            root_locale="ru",
        )

    def get_translator(self, language: str, *args, **kwargs) -> LocalizedTranslator:
        """
        The get_translator function is a method of the LocalizedTranslatorFactory class.
        It takes in a language string and returns an instance of the LocalizedTranslator class, which is initialized with
        a translator object from the TranslatorHub. The TranslatorHub is initialized with all available languages, so it can
        return any translator that has been loaded into it.

        :param self: Used to Represent the instance of the class.
        :param language:str: Used to Specify the language that we want to translate our text into.
        :param *args: Used to Send a non-keyworded variable length argument list to the function.
        :param **kwargs: Used to Pass a variable number of keyword arguments to the function.
        :return: A localizedtranslator object.

        """
        return LocalizedTranslator(
            translator=self.t_hub.get_translator_by_locale(locale=language)
        )


usr_lang = {}


# path to file
def image_to_pdf(path: str) -> None:
    """
    The image_to_pdf function takes a path to an image file and converts it into a PDF.
    The function uses the Pillow library to open the image, convert it from RGBA (the default)
    to RGB, and then save it as a PDF with the same name as the original file but with .pdf
    appended at the end of its name.

    :param path:str: Used to Specify the path of the image file.
    :return: None.
    """
    image = Image.open(path)
    image = image.convert("RGB")
    if (idx := path.rfind("."), -5) != -1:
        path = path[:idx]
    path += ".pdf"
    image.save(path)


def make_notebook(file_name: str, usr_id: int) -> None:
    """
    The make_notebook function takes in a file_name and user id.
    It then creates a path to the user's directory, finds all files that start with the user's id,
    and converts any non-pdf files into pdfs. It then merges all of these pdfs together into one notebook.

    :param file_name:str: Used to Name the file that will be created.
    :param usr_id:int: Used to Identify the user and create a folder for them.
    :return: None
    """
    path = f"{__file__[:-8]}/usr_files/{usr_id}/"
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
    The update_notebook function takes in a file name and user id. It then creates a list of all the pdf files
    in the user's directory, appends the new pdf to that list, and merges them together into one notebook.

    :param file_name:str: Used to Name the file that is created.
    :param usr_id:int: Used to Identify the user's folder.
    :return: None.
    """
    path = f"{__file__[:-8]}/usr_files/{usr_id}/"
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
        """
        The __call__ function is a coroutine that takes in the following arguments:
            handler: A function that handles the event.
            event: The Telegram message or callback query object.
            data: A dictionary of data to pass to the handler function.

        :param self: Used to Access the instance of the class.
        :param handler:Callable[[Message: Used to Pass the message to the handler.
        :param Dict[str: Used to Store data that is passed to the handler function.
        :param Any]]: Used to Specify the return type of the handler function.
        :param Awaitable[Any]]: Used to Define the return type of the handler function.
        :param event:Union[Message: Used to Pass the message object to the handler.
        :param CallbackQuery]: Used to Pass the event object to the handler function.
        :param data:Dict[str: Used to Pass data from the previous handler to the next one.
        :param Any]: Used to Specify the return type of the handler function.
        :param : Used to Pass the handler function to the decorator.
        :return: The handler function.

        """
        return await handler(event, data)


async def download_file(url: str, destination_path: str, file_name: str) -> None:
    """
    The download_file function downloads a file from the given url and saves it to the destination_path with
    the given file_name.

    :param url:str: Used to Specify the url of the file to be downloaded.
    :param destination_path:str: Used to Specify the directory where the file will be downloaded to.
    :param file_name:str: Used to Name the file,.
    :return: None, because there is no return statement in the function.
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
    The command_start function is the first function that is called when a user
    starts interacting with the bot. It creates a folder for each user in which all
    the files will be stored. The language of interaction is set to English by default.

    :param message:types.Message: Used to Get the user id and to send a message back.
    :return: A message with the keyboard.
    """
    user_id = message.from_user.id
    if "usr_files" not in os.listdir(f"{__file__[:-8]}"):
        os.mkdir(f"{__file__[:-8]}/usr_files")

    if str(user_id) not in os.listdir(f"{__file__[:-8]}/usr_files/"):
        os.mkdir(f"{__file__[:-8]}/usr_files/{user_id}")
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
    The command_help function is a command handler that takes in a message and
    a CommandObject. It then loops through the bot_commands list of tuples, looking
    for the tuple whose first element matches the argument passed to /help. If it finds
    it, it returns an answer to the user with that command's name and description. If not,
    it returns an error message.

    :param message:types.Message: Used to Get the message object that was sent by the user.
    :param command:CommandObject: Used to Get the command name.
    :return: A message with the help for a specific command.
    """
    for cmd in bot_commands:
        if cmd[0] == command.args:
            return await message.answer(text=f"{cmd[0]} - {cmd[1]}")

    return await message.answer(
        text=f"Command {command.args} not found. \n\n use /help <command>"
    )


async def choose_lang(message: types.Message, translator: Translator) -> None:
    """
    The choose_lang function is used to set the language of the bot for a specific user.
    It takes in two arguments: message and translator. The message argument is an object that contains information about
    the user's request, such as their id, username, etc. The translator argument is an object that allows us to translate
    text into different languages using Google Translate API.

    :param message:types.Message: Used to Get the message from the user.
    :param translator:Translator: Used to Get the translator object.
    :return: The language that the user has chosen.
    """
    trans = translator.get_translator(language=message.text.lower())
    t = trans.get("test")
    usr_lang[message.from_user.id] = message.text.lower()
    await message.answer(text=f"{t} + You choose {message.text}")


async def get_menu(message: types.Message) -> None:
    """
    The get_menu function is used to display the main menu of the bot.
    It is called when a user sends /start or /menu commands.

    :param message:types.Message: Used to Access the message object.
    :return: A menu with buttons.
    """
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
    The get_new_file_name function is a coroutine that is called when the user wants to add a new notebook.
    It sets the state of the FSMContext object to waiting_for_name, which means that it will wait for an input from
    the user. It then sends a message asking for the name of this new notebook and provides them with an option to cancel.

    :param message:types.Message: Used to Get the message sent by the user.
    :param state:FSMContext: Used to Store the state of the conversation.
    :return: The name of the notebook.
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
    The add_new_file function is the first step in adding a new file to the database.
    It takes in a message, state and translator as arguments. The function then checks if
    the user has cancelled their request by checking if they have sent "Cancel" as their
    message text. If so, it clears the state and returns nothing (None). Otherwise, it updates
    the data with what is currently stored in name (which should be an empty string) and sets
    the current state to waiting_for_file using set_state(). It then creates a cancel board which is used for cancelling requests at any point during this process. It also gets the translator for that specific language from usr_lang[message.from_user] which stores all of our users' languages based on their ID's so we can translate messages into different languages depending on who sends them! Finally, it sends back a message asking them to upload/send over whatever file they want added along with our cancel board.

    :param message:types.Message: Used to Get the message that was sent by the user.
    :param state:FSMContext: Used to Store the state of the conversation.
    :param translator:Translator: Used to Translate the message to the user's language.
    :return: The file.
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
    The get_new_file function is the first step in creating a new notebook.
    It takes a message from the user and checks if it is either text or an attachment.
    If it is text, then we check if that text is "Cancel". If so, we clear our state and return to the main menu.
    Otherwise, we set our state to creating_notebook (which will be used later) and wait for 20 seconds before calling
    the create_new_notebook function which will actually create our notebook.

    :param message:types.Message: Used to Get the message sent by the user.
    :param state:FSMContext: Used to Store the state of the bot.
    :return: A file.
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
        destination_path=f"{__file__[:-8]}/usr_files/{message.from_user.id}",
        file_name=file_name,
    )


async def create_new_notebook(message: types.Message, state: FSMContext) -> None:
    """
    The create_new_notebook function is called when the user has finished entering their notebook name.
    It takes in a message and state, which is used to get the data from the previous step.
    The function then uses that data to create a new notebook with that name for that user.

    :param message:types.Message: Used to Get the message sent by the user.
    :param state:FSMContext: Used to Store the data from the previous state.
    :return: Nothing.
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
    The show_user_notebooks function is used to show the user all of their notebooks.
    It is called when the user presses on the 'Show Notebooks' button in the main menu.
    The function first checks if there are any notebooks for this particular user, and if not, it clears
    the state and returns None (meaning that nothing happens). If there are notebooks for this particular
    user, then we set our state to waiting_for_choose (which means that we're waiting for a callback query),
    and then create an InlineKeyboardBuilder object which will be used to build our inline keyboard markup. We loop through all of our files in usr_files/usr_id/, where usr_id is equal to message.from_user.id (which means that it's equal to the id of whoever sent this message). For each file in files, we split its name by "." so as not only get its name but also its extension (.txt or .json) - since we don't want those extensions showing up on our buttons! Then, using InlineKeyboardBuilder's button method with text=file[0] and callback data=file[0], meaning that both text and callback data will be equal to whatever file was

    :param message:types.Message: Used to Get the user's message.
    :param state:FSMContext: Used to Keep track of the state of a user.
    :param translator:Translator: Used to Translate the text to the user's language.
    :return: A list of user notebooks.
    """
    usr_id = message.from_user.id
    files = [
        file
        for file in os.listdir(f"{__file__[:-8]}/usr_files/{usr_id}/")
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
    The send_notebook function is called when the user clicks on a file in their list of files.
    It sends the file to them.

    :param callback:types.CallbackQuery: Used to Get the callback data from the button that was pressed.
    :param state:FSMContext: Used to Store the state of the bot.
    :return: None.
    """
    await state.clear()
    files = os.listdir(f"{__file__[:-8]}/usr_files/{callback.from_user.id}/")
    for file in files:
        if file.startswith(callback.data):
            file_obj = FSInputFile(
                f"{__file__[:-8]}/usr_files/{callback.from_user.id}/{file}"
            )
            await SendDocument(chat_id=callback.message.chat.id, document=file_obj)
            break


# ========================== Changing user files ==========================


async def changing_user_notebook(
    message: types.Message, state: FSMContext, translator: Translator
) -> None:
    """
    The changing_user_notebook function is used to change the user's notebook.
    It is called when the user presses the "Change" button in his/her menu.
    The function first sets a state for this conversation, which will be used later on to determine what action should be taken next.
    Then it checks if there are any notebooks created by this user and if not, clears all states and returns nothing (the conversation ends).
    If there are notebooks created by this user, then it creates a keyboard with buttons corresponding to each of these notebooks' names (file names)
    and sends that keyboard along with an explanatory message as a reply.

    :param message:types.Message: Used to Get the user id.
    :param state:FSMContext: Used to Store the state of a user.
    :param translator:Translator: Used to Translate the text in the message.
    :return: The name of the file to be changed.
    """
    await state.set_state(ChangingStates.waiting_for_name)
    usr_id = message.from_user.id
    files = [
        file
        for file in os.listdir(f"{__file__[:-8]}/usr_files/{usr_id}/")
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
    The get_change_to_notebook function is a coroutine that is called when the user
    wants to change the name of a notebook. It takes in three arguments: message, state, and translator.
    The message argument is an instance of types.Message from pyTelegramBotAPI which contains information about
    the Telegram message sent by the user (e.g., text). The state argument is an instance of FSMContext from
    aiogram's FSMContext class which allows us to access and update data stored in our bot's database for this particular chat session with this particular user (e.g., what notebook they are currently viewing). The translator argument is an instance of Translator from googletrans' Translator class which allows us to translate strings into different languages based on what language we specify as its first parameter.

    :param message:types.Message: Used to Get the message that was sent by the user.
    :param state:FSMContext: Used to Store the state of the conversation.
    :param translator:Translator: Used to Translate the text to the user's language.
    :return: The user's choice of notebook to change.
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
    The get_files_to_update function is used to get the files that the user wants to update.
    It is called when a user sends a file or photo in response to the bot's request for files.
    The function checks if it is an image or document and then downloads it from Telegram's servers,
    saving it in usr_files/{user_id}/{file_name}. It also saves information about this file into
    the state object so that we can access this information later.

    :param message:types.Message: Used to Get the message sent by the user.
    :param state:FSMContext: Used to Pass the state of the conversation to this function.
    :return: The files to be updated.
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
        destination_path=f"{__file__[:-8]}/usr_files/{message.from_user.id}",
        file_name=file_name,
    )


async def make_changes(message: types.Message, state: FSMContext) -> None:
    """
    The make_changes function is the final step in our state machine.
    It takes a message and a state, which is passed from the previous function.
    The data that was stored in the previous function is retrieved using get_data().
    Then we update our notebook with this new information.

    :param message:types.Message: Used to Get the message that was sent by the user.
    :param state:FSMContext: Used to Store the data between different states.
    :return: Nothing.
    """
    data = await state.get_data()

    await message.answer(text=f"Starting adding to {data['name']}")

    update_notebook(f'{data["name"]}', message.from_user.id)
    await message.answer(text=f"{data['name']} complete")
    

def register_user_commands(router: Router) -> None:
    """
    The register_user_commands function is used to register all the user commands.
    It takes a router as an argument and registers all the functions that are needed for
    the bot to work properly. It also uses some of the classes from states module, which
    are used in order to make sure that bot is working correctly.

    :param router:Router: Used to Register the user's commands.
    :return: None.
    """
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
    """
    The main function of the bot.

    This function is called when the bot starts up, and it registers all of its handlers. It also sets up a Dispatcher object to handle incoming updates from Telegram, and passes that dispatcher to the updater's start_polling method. This will cause our bot to start polling for updates from Telegram indefinitely until we stop it by calling updater.stop().

    :return: None.
    """
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
    """
    The run_bot function is the start up function of the bot.

    :return: None.
    """
    asyncio.run(main())


if __name__ == "__main__":
    run_bot()
