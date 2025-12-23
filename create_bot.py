import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage


logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
logger = logging.getLogger(__name__)

load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")
WIFE_CHAT_ID = int(os.getenv("WIFE_CHAT_ID", "0"))

bot = Bot(token=API_TOKEN, default_bot_properties=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())






