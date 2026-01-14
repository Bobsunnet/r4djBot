import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


class TelegramSettings(BaseSettings):
    bot_token: str = os.getenv("BOT_TOKEN")
    manager_id: int = int(os.getenv("MANAGER_ID", "0"))


class DbSettings(BaseSettings):
    db_url: str = os.getenv("DB_URL")
    echo: bool = os.getenv("ECHO", "False").lower() in ("true", "1")
    sync_db: bool = os.getenv("SYNC_DB", "False").lower() in ("true", "1")
    sync_db_interval: int = int(os.getenv("SYNC_DB_INTERVAL", "False"))


class Settings(BaseSettings):
    telegram: TelegramSettings = TelegramSettings()
    db: DbSettings = DbSettings()
    debug: bool = os.getenv("DEBUG", "False").lower() in ("true", "1")
    LOG_DIR: Path = BASE_DIR / "logs"
    web_app_url: str = os.getenv("WEB_APP_URL")
    price_multiplier: float = 0.5


settings = Settings()
