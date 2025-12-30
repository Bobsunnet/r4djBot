import asyncio

from create_bot import bot, dp, set_commands
from handlers import contacts_router, order_router, start_router


async def main():
    dp.include_router(start_router)
    dp.include_router(contacts_router)
    dp.include_router(order_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await set_commands()
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped manually.")
