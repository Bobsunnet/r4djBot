import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_ID = int(os.getenv("MANAGER_ID", "0"))
WIFE_CHAT_ID = int(os.getenv("WIFE_CHAT_ID", "0"))
VADOS_CHAT_ID = int(os.getenv("VADOS_CHAT_ID", "0"))

DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1")

LOG_DIR = BASE_DIR / "logs"

# Business Logic
PRICE_MULTIPLIER = 0.5

reload_help_message = "Спробуйте ще раз, перезавнтаживши бота командою /start"
