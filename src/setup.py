from aiogram.utils import executor
from bot import bot, dp
from config import ADMIN_ID

from handlers.client import register_handlers

register_handlers(dp)


async def start_admin(_):
    await bot.send_message(chat_id=ADMIN_ID, text="Starting bot...")


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=start_admin)
