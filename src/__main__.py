import asyncio
import logging
from aiogram import Dispatcher, Bot
from aiogram.types import BotCommand

from config import BOT_TOKEN
from handlers import register_user_commands, bot_commands


async def main():
    logging.basicConfig(level=logging.DEBUG)

    dp = Dispatcher()
    bot = Bot(token=BOT_TOKEN)

    register_user_commands(dp)

    await bot.set_my_commands(
        commands=[BotCommand(command=cmd[0], description=cmd[1]) for cmd in bot_commands]
    )

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped")
