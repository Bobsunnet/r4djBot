import logging

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from db_handler.db_class import db_handler
from keyboards import (
    make_auth_kb,
    make_confirmation_kb,
    make_share_contact_kb,
    make_wo_auth_kb,
)

logger = logging.getLogger(__name__)


class Registration(StatesGroup):
    name = State()
    phone = State()


start_router = Router()


# --------------- MENU HANDLERS -----------------------------------


# @start_router.message()
# async def unknown_command(message: Message):
#     await message.answer("Невідома команда")


@start_router.message(CommandStart())
async def cmd_start(message: Message):
    user = db_handler.read_user_by_user_id(message.from_user.id)
    if user:
        reply_text = f"Вітаємо, {user['name']}. Оберіть одну з команд:"
        await message.answer(reply_text, reply_markup=make_auth_kb())
    else:
        reply_text = "Вітаємо. На жаль, ви ще не зареєстровані в системі. Пройдіть швидку реєстрацію."
        await message.answer(reply_text, reply_markup=make_wo_auth_kb())


@start_router.message(F.text.lower() == "register")
async def start_registration(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Registration.name)
    await message.answer("Введіть ваше ім'я")


@start_router.message(Registration.name, F.text)
async def registration_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Registration.phone)
    await message.answer(
        "Надайте доступ до ваших контактів, натиснувши кнопку",
        reply_markup=make_share_contact_kb(),
    )


@start_router.message(Registration.phone, F.contact)
async def registration_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    data = await state.get_data()
    try:
        db_handler.create_user(
            user_id=message.from_user.id,
            name=data["name"],
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            phone_number=data["phone"],
        )

        await message.answer("Дякуємо за реєстрацію!", reply_markup=make_auth_kb())

    except Exception as e:
        logger.error(f"Error {e}. Failed to register user: {message.from_user}")
        await message.answer("Помилка реєстрації, спробуйте ще раз")
    finally:
        await state.clear()


# ------------------------- F.text hadnlers ------------------------


@start_router.message(F.text.lower() == "catalogue")
async def cmd_catalogue(message: Message):
    await message.answer(
        "📄 Каталог обладнання: https://docs.google.com/spreadsheets/d/1ez7Ur5YD0AiTtN2QEWcgZyhlqLGAA6gln0BgTcbBDqM/edit?gid=0#gid=0"
    )
