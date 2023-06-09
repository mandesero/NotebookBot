import pytest
from unittest.mock import AsyncMock

from aiogram.utils.keyboard import ReplyKeyboardBuilder

from src.handlers.client import command_start


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
