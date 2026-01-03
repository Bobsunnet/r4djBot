import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault
from dotenv import load_dotenv

load_dotenv()

import log_setup  # must be first to configure logging  # noqa: F401

logger = logging.getLogger(__name__)


BOT_TOKEN = os.getenv("BOT_TOKEN")
WIFE_CHAT_ID = int(os.getenv("WIFE_CHAT_ID", "0"))

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())


async def set_commands():
    my_commands = [
        BotCommand(command="start", description="Розпочати роботу"),
    ]
    await bot.set_my_commands(commands=my_commands, scope=BotCommandScopeDefault())


async def on_startup():
    logger.info("Bot is starting...")


dp.startup.register(on_startup)
