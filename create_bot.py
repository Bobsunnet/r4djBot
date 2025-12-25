import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WIFE_CHAT_ID = int(os.getenv("WIFE_CHAT_ID", "0"))

bot = Bot(
    token=BOT_TOKEN, default_bot_properties=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher(storage=MemoryStorage())


async def set_commands():
    commands = [
        BotCommand(command="start", description="start"),
        BotCommand(command="start_2", description="start_2"),
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def on_startup():
    logger.info("Bot is starting...")


dp.startup.register(on_startup)
