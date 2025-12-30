from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from db_handler import db_handler
from keyboards import create_inline_kb, make_main_kb
from utils import get_random_user

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
        "HEre is your inline keyboard message", reply_markup=create_inline_kb()
    )


# ----------------------- CALLBACK_QUERIES ------------------------------
@start_router.callback_query(F.data == "gen_user")
async def send_random_person(call: CallbackQuery):
    await call.answer("generating random user", show_alert=False)
    user = get_random_user()
    formatted_msg = (
        f"<b>Name:</b> {user['name']}\n"
        f"<b>Phone:</b> {user['phone']}\n"
        f"<b>Adress:</b> {user['adress']}\n"
        f"<b>Company:</b> {user['company']}\n"
    )
    await call.message.answer(formatted_msg)


@start_router.callback_query(F.data == "back_home")
async def cmd_home(call: CallbackQuery):
    await call.answer()
    await call.message.answer("/start")


# @start_router.callback_query(F.data.startswith("qst_"))
# async def cmd_qsts(call: CallbackQuery):
#     await call.answer()
#     qst_id = int(call.data.split("_")[1])
#     qst_data = questions[qst_id]
#     msg_text = (
#         f"Question {qst_data.get('qst')} answer\n\n"
#         f"<b>{qst_data.get('answer')}</b>\n\n"
#         f"Chose another question:"
#     )

#     async with ChatActionSender(bot=bot, chat_id=call.from_user.id, action="typing"):
#         await asyncio.sleep(1)
#         await call.message.answer(msg_text, reply_markup=create_qst_kb())
