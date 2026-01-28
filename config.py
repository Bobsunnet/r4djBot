import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

DAY_IN_SECONDS = 86400

TRUE_VALUES = ("true", "1")


class TelegramSettings(BaseSettings):
    bot_token: str = os.getenv("BOT_TOKEN")
    manager_id: int = int(os.getenv("MANAGER_ID", "0"))
    disable_notification: bool = (
        os.getenv("DISABLE_NOTIFICATION", "False").lower() in TRUE_VALUES
    )


class CacheSettings(BaseSettings):
    js_cache_ttl: int = int(os.getenv("JS_CACHE_TTL", DAY_IN_SECONDS))


class DbSettings(BaseSettings):
    db_url: str = os.getenv("DB_URL")
    echo: bool = os.getenv("ECHO", "False").lower() in TRUE_VALUES
    sync_db: bool = os.getenv("SYNC_DB", "False").lower() in TRUE_VALUES
    sync_db_interval: int = int(os.getenv("SYNC_DB_INTERVAL", "60"))


class Settings(BaseSettings):
    telegram: TelegramSettings = TelegramSettings()
    cache: CacheSettings = CacheSettings()
    db: DbSettings = DbSettings()
    debug: bool = os.getenv("DEBUG", "False").lower() in TRUE_VALUES
    LOG_DIR: Path = BASE_DIR / "logs"
    web_app_url: str = os.getenv("WEB_APP_URL")
    price_multiplier: float = 0.5


settings = Settings()
