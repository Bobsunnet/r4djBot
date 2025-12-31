import asyncio
import logging

from create_bot import bot, dp, set_commands
from handlers import contacts_router, order_router, start_router

logging.basicConfig(level=logging.INFO)


async def main():
    # Include routers
    dp.include_router(start_router)
    dp.include_router(contacts_router)
    dp.include_router(order_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await set_commands()

    # Start API server and bot concurrently
    from utils.api_server import start_server

    async def run_bot():
        await dp.start_polling(bot)

    async def run_web_server():
        await start_server(host="0.0.0.0", port=8080)

    await asyncio.gather(run_web_server(), run_bot())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped manually.")
