from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from keyboards import make_main_kb, create_spec_kb
from db_handler import db_handler


start_router = Router()


@start_router.message(CommandStart())
async def cmd_start(message: Message):
    print(f"Start command invoked. Uer_id: {message.from_user.id}")
    await message.answer("Hi, im /start comand handler!", reply_markup=make_main_kb())


@start_router.message(F.text.lower() == "catalogue")
async def cmd_catalogue(message: Message):
    res = db_handler.read_all()[23:27]
    await message.answer(
        "Here is our catalogue: \n"
        + "\n".join([f"{item[1]}. {item[2]} - {item[3]}" for item in res])
    )


@start_router.message(Command("start_2"))
async def cmd_start_2(message: Message):
    await message.answer("start_2 command", reply_markup=create_spec_kb())
