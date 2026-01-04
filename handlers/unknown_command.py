from aiogram import Router
from aiogram.types import Message

unknown_command_router = Router()


@unknown_command_router.message()
async def unknown_command(message: Message):
    await message.answer("Невідома команда, введіть /start")
