import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault

import log_setup  # noqa: F401
from config import settings

logger = logging.getLogger(__name__)

bot = Bot(
    token=settings.telegram.bot_token, default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher(storage=MemoryStorage())


async def set_commands():
    my_commands = [
        BotCommand(command="start", description="Розпочати роботу"),
        BotCommand(command="help", description="Інформація про роботу з ботом"),
    ]
    await bot.set_my_commands(commands=my_commands, scope=BotCommandScopeDefault())


async def on_startup():
    logger.info("Bot is starting...")


dp.startup.register(on_startup)
