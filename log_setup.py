import logging
import os
from logging.handlers import RotatingFileHandler

DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
formatter = logging.Formatter(LOG_FORMAT)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

if DEBUG:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

all_logs_handler = RotatingFileHandler(
    filename=os.path.join(LOG_DIR, "bot.log"),
    maxBytes=1024 * 1024 * 5,
    backupCount=3,
    encoding="utf-8",
)

all_logs_handler.setLevel(logging.INFO)
all_logs_handler.setFormatter(formatter)

error_logs_handler = RotatingFileHandler(
    filename=os.path.join(LOG_DIR, "error.log"),
    maxBytes=1024 * 1024 * 5,
    backupCount=5,
    encoding="utf-8",
)

error_logs_handler.setLevel(logging.ERROR)
error_logs_handler.setFormatter(formatter)

root_logger.addHandler(all_logs_handler)
root_logger.addHandler(error_logs_handler)

logger = logging.getLogger(__name__)
