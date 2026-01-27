import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from db_handler.crud import get_user_by_tg_id
from filters import TextOrCommand
from keyboards import (
    make_auth_kb,
    make_wo_auth_kb,
)
from utils import messages as ms

logger = logging.getLogger(__name__)


start_router = Router()


def format_welcome_message(name: str) -> str:
    """
    Formats the welcome message for the user.
    """
    return f"Вітаємо, {name}. Оберіть одну з команд /catalogue, /contacts, /order:"


# --------------- MENU HANDLERS -----------------------------------


@start_router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession):
    user = await get_user_by_tg_id(
        session=session,
        user_id=message.from_user.id,
    )
    if user:
        reply_text = format_welcome_message(user.name)
        await message.answer(reply_text, reply_markup=make_auth_kb())
    else:
        reply_text = "Вітаємо. " + ms.not_authorized_message
        await message.answer(reply_text, reply_markup=make_wo_auth_kb())


# ------------------------- F.text hadnlers ------------------------


@start_router.message(TextOrCommand("catalogue"))
async def cmd_catalogue(message: Message):
    await message.answer(
        "📄 Каталог обладнання: https://docs.google.com/spreadsheets/d/1ez7Ur5YD0AiTtN2QEWcgZyhlqLGAA6gln0BgTcbBDqM/edit?gid=0#gid=0"
    )
