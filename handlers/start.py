from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards import make_main_kb, order_inline_kb

start_router = Router()


# --------------- MENU HANDLERS -----------------------------------


@start_router.message(CommandStart())
async def cmd_start(message: Message):
    print(f"Start command invoked. Uer_id: {message.from_user.id}")

    await message.answer(
        "Привіт, розпочато роботу з ботом. Обери одну з команд",
        reply_markup=make_main_kb(),
    )


# ------------------------- F.text hadnlers ------------------------


@start_router.message(F.text.lower() == "catalogue")
async def cmd_catalogue(message: Message):
    await message.answer(
        "📄 Каталог обладнання: https://docs.google.com/spreadsheets/d/1ez7Ur5YD0AiTtN2QEWcgZyhlqLGAA6gln0BgTcbBDqM/edit?gid=0#gid=0"
    )


@start_router.message(F.text.lower() == "/order")
async def cmd_inline_test(message: Message):
    await message.answer(
        "Тут ви можете вибрати з катаологу обладнання та оформити замовлення",
        reply_markup=order_inline_kb(),
    )
