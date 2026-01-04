import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault

import config
import log_setup  # noqa: F401

logger = logging.getLogger(__name__)

bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())


async def set_commands():
    my_commands = [
        BotCommand(command="start", description="Розпочати роботу"),
    ]
    await bot.set_my_commands(commands=my_commands, scope=BotCommandScopeDefault())


async def on_startup():
    logger.info("Bot is starting...")
    # await bot.send_message(config.WIFE_CHAT_ID, "Йо, нажми /start")


dp.startup.register(on_startup)
