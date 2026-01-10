from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

help_router = Router()


help_message = """Цей бот призначений для створення запитів на оренду обладнання в RENT4DJ. 
Щоб розпочати роботу використовуйте команду /start
*Команда /catalogue відправляє до таблиці зі списком обладнання
*Команда /contacts відправляє повідомлення з контактною інформацією
*Команда /order дозволяє створити запит на оренду обладнання"""


@help_router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(help_message)
