import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from filters import TextOrCommand
from keyboards import (
    make_auth_kb,
    make_wo_auth_kb,
)
from utils import messages as ms
from utils.db_utils import get_authorized_user
from utils.utils import format_welcome_message

logger = logging.getLogger(__name__)


start_router = Router()


# --------------- MENU HANDLERS -----------------------------------


@start_router.message(CommandStart())
async def cmd_start(message: Message):
    user = get_authorized_user(message.from_user.id)
    if user:
        reply_text = format_welcome_message(user["name"])
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
