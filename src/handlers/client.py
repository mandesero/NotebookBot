from aiogram import types
from aiogram.filters import CommandObject

from keyboards.client_kb import lang_kb

bot_commands = {
    ("start", "start messaging with bot",),
    ("help", "get some help",)
}


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
