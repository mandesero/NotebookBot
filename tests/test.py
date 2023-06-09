import pytest
from unittest.mock import AsyncMock

from aiogram.utils.keyboard import ReplyKeyboardBuilder

from src.handlers.client import get_menu


@pytest.mark.asyncio
async def test_start_handler():
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
