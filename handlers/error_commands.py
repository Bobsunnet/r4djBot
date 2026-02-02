from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from aiogram_calendar import SimpleCalendarCallback
from keyboards import make_user_kb

unknown_command_router = Router()


@unknown_command_router.message(F.web_app_data)
async def web_app_data_stateless(message: Message):
    await message.answer(
        "Стався збій при формуванні замовлення, спробуйте ще раз з команди /start",
        reply_markup=make_user_kb(),
    )


@unknown_command_router.message()
async def unknown_command(message: Message):
    await message.answer("Невідома команда, введіть /start")


@unknown_command_router.callback_query(SimpleCalendarCallback.filter())
async def stateless_simple_calendar_callback(callback_query: CallbackQuery):
    await callback_query.message.delete()
    await callback_query.answer("Стався збій при формуванні замовлення, спробуйте ще раз з команди /start")
