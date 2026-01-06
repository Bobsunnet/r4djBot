from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

help_router = Router()


help_message = """Інфа про роботу з ботом....[Скоро доповниться]. 
Щоб розпочати роботу використовуйте команду /start"""


@help_router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(help_message)
