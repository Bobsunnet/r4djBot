from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from db_handler import db_handler
from keyboards import make_main_kb, order_inline_kb

start_router = Router()


# --------------- MENU HANDLERS -----------------------------------


@start_router.message(CommandStart())
async def cmd_start(message: Message):
    print(f"Start command invoked. Uer_id: {message.from_user.id}")

    await message.answer("Hi, im /start comand handler!", reply_markup=make_main_kb())


# ------------------------- F.text hadnlers ------------------------


@start_router.message(F.text.lower() == "catalogue")
async def cmd_catalogue(message: Message):
    res = db_handler.read_all()[23:27]
    await message.answer(
        "Here is our catalogue: \n"
        + "\n".join([f"{item[1]}. {item[2]} - {item[3]}" for item in res])
    )


@start_router.message(F.text.lower() == "/inline")
async def cmd_inline_test(message: Message):
    await message.answer(
        "HEre is your inline keyboard message", reply_markup=order_inline_kb()
    )
