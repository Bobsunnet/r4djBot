import asyncio
import logging

from create_bot import bot, dp, set_commands
from db_handler.bulk_operations import bulk_insert_items, create_db
from handlers import *
from middlewares.db import DbSessionMiddleware
from schedulers.schedulers import scheduler_setup

logger = logging.getLogger(__name__)


async def startup_db():
    await create_db()
    await bulk_insert_items()


async def main():
    await startup_db()

    dp.update.middleware(DbSessionMiddleware())
    dp.include_router(start_router)
    dp.include_router(help_router)
    dp.include_router(contacts_router)
    dp.include_router(register_router)
    dp.include_router(order_router)
    dp.include_router(user_private_router)
    dp.include_router(manager_router)
    dp.include_router(details_router)
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
