import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_ID = int(os.getenv("MANAGER_ID", "0"))
WIFE_ID = int(os.getenv("WIFE_ID", "0"))
VADOS_ID = int(os.getenv("VADOS_ID", "0"))
WEB_APP_URL = os.getenv("WEB_APP_URL")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1")
SYNC_DB = os.getenv("SYNC_DB", "False").lower() in ("true", "1")
LOG_DIR = BASE_DIR / "logs"
SYNC_DB_INTERVAL = int(os.getenv("SYNC_DB_INTERVAL", "False"))

# Business Logic
PRICE_MULTIPLIER = 0.5

reload_help_message = "Спробуйте ще раз, перезавнтаживши бота командою /start"
