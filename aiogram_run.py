import asyncio
import logging

from create_bot import bot, dp, set_commands
from db_handler.models import db_helper
from db_handler.models.base import Base
from handlers import (
    contacts_router,
    help_router,
    order_router,
    register_router,
    start_router,
    unknown_command_router,
)
from middlewares.db import DbSessionMiddleware
from schedulers.schedulers import scheduler_setup

logger = logging.getLogger(__name__)


async def create_test_db():
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def main():
    await create_test_db()

    dp.update.middleware(DbSessionMiddleware())
    dp.include_router(start_router)
    dp.include_router(help_router)
    dp.include_router(contacts_router)
    dp.include_router(register_router)
    dp.include_router(order_router)
    dp.include_router(unknown_command_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await set_commands()

    # Start API server and bot concurrently
    from utils.api_server import start_server

    async def run_bot():
        await dp.start_polling(bot)

    async def run_web_server():
        await start_server(host="127.0.0.1", port=8000)

    scheduler_setup()

    await asyncio.gather(run_web_server(), run_bot())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("Bot stopped manually.")
