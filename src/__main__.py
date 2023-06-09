import asyncio
import logging
from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import BOT_TOKEN
from handlers import register_user_commands, bot_commands
from languages.translator import Translator


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


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped")
