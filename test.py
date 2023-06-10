import pytest
from unittest.mock import AsyncMock

from aiogram.utils.keyboard import ReplyKeyboardBuilder

from src.main import get_menu, command_help, command_start


@pytest.mark.asyncio
async def test_menu_handler():
    message = AsyncMock()
    await get_menu(message)

    menu_markup = ReplyKeyboardBuilder()
    menu_markup.button(text="Add new file", callback_data="add_new_file")
    menu_markup.button(text="Change file", callback_data="change_file")
    menu_markup.button(text="Show my notebooks", callback_data="show_notebooks")
    menu_markup.adjust(1)

    message.answer.assert_called_with(
        text="Menu",
        reply_markup=menu_markup.as_markup(
            resize_keyboard=True, one_time_keyboard=True
        ),
    )


@pytest.mark.asyncio
async def test_start_handler():
    message = AsyncMock()
    await command_start(message)

    lang_markup = ReplyKeyboardBuilder()
    lang_markup.button(text="ru", callback_data="ru")
    lang_markup.button(text="en", callback_data="en")
    lang_markup.adjust(2)

    message.answer.assert_called_with(
        text="Hello",
        reply_markup=lang_markup.as_markup(
            resize_keyboard=True, one_time_keyboard=True
        ),
    )


@pytest.mark.asyncio
async def test_help_handler_1():
    message = AsyncMock()
    command = AsyncMock()
    command.args = "TEST COMMAND"
    await command_help(message, command)
    message.answer.assert_called_with(
        text="Command TEST COMMAND not found. \n\n use /help <command>"
    )


@pytest.mark.asyncio
async def test_help_handler_2():
    message = AsyncMock()
    command = AsyncMock()
    command.args = "help"
    await command_help(message, command)
    message.answer.assert_called_with(text="help - get some help")
