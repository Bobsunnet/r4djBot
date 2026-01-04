import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

import config
from db_handler.db_class import db_handler
from keyboards import make_auth_kb, make_share_contact_kb

logger = logging.getLogger(__name__)

register_router = Router()


class Registration(StatesGroup):
    name = State()
    phone = State()


def is_valid_number(phone_number: str) -> bool:
    return (
        phone_number.startswith("+380")
        and len(phone_number) == 13
        and phone_number[1:].isdigit()
    )


@register_router.message(F.text.lower() == "register")
async def start_registration(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Registration.name)
    await message.answer("Введіть ваше ім'я")


@register_router.message(Registration.name, F.text)
async def registration_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Registration.phone)
    await message.answer(
        "Поділіться вашим номером телефону, натиснувши кнопку внизу. Це необхідно для зворотнього зв'язку з вами.",
        reply_markup=make_share_contact_kb(),
    )


@register_router.message(Registration.phone, F.contact | F.text)
async def registration_phone(message: Message, state: FSMContext):
    if message.contact:
        await state.update_data(phone=message.contact.phone_number)
    else:
        if is_valid_number(message.text):
            await state.update_data(phone=message.text)
        else:
            await state.set_state(Registration.phone)
            await message.answer(
                'Не корректний номер телефону. Якщо вже пишите "руками", то пишіть повний формат номеру,'
                'наприклад: "+380991234567". А краще скористайтеся кнопкою внизу: "Поділитися контактом"'
            )
            return

    data = await state.get_data()
    try:
        db_handler.create_user(
            user_id=message.from_user.id,
            name=data["name"],
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            phone_number=data["phone"],
        )

        await message.answer(
            f"Дякуємо за реєстрацію, {data['name']}!", reply_markup=make_auth_kb()
        )

    except Exception as e:
        logger.error(f"Error {e}. Failed to register user: {message.from_user}")
        await message.answer(f"Помилка реєстрації, {config.reload_help_message}")
    finally:
        await state.clear()
