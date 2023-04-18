from aiogram import types

from keyboards.client_kb import lang_kb


async def command_start(message: types.Message) -> None:
    """
    Start messaging with bot. Ability to set locale.

    :param message: command "/start"
    :return: None
    """
    await message.answer(
        "Hello",
        reply_markup=lang_kb.as_markup(
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


async def command_help(message: types.Message) -> None:
    """
    Command for get some help.

    :param message: command "/help"
    :return: None
    """
    await message.answer(text="Help")


async def choose_lang(message: types.Message) -> None:
    """
    Set up user locale.

    :param message: locale ["ru" | "eng"]
    :return: None
    """
    await message.answer(text=f"You choose {message.text}")
