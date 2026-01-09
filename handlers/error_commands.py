from aiogram import F, Router
from aiogram.types import Message

from keyboards import make_auth_kb

unknown_command_router = Router()


@unknown_command_router.message(F.web_app_data)
async def web_app_data_stateless(message: Message):
    await message.answer(
        "Стався збій при формуванні замовлення, спробуйте ще раз з команди /start",
        reply_markup=make_auth_kb(),
    )


@unknown_command_router.message()
async def unknown_command(message: Message):
    await message.answer("Невідома команда, введіть /start")
