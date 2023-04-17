import asyncio
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from .config import BOT_TOKEN

loop = asyncio.get_event_loop()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, loop=loop, storage=(storage := MemoryStorage()))
