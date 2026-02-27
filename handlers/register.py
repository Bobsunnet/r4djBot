import logging

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db_handler import crud
from db_handler.schemas.user import UserCreate
from keyboards import (
    make_cancel_kb,
    make_share_contact_kb,
    make_user_kb,
    make_wo_auth_kb,
)
from utils import messages as ms
from utils.utils import is_valid_number, validate_name

logger = logging.getLogger(__name__)

register_router = Router()


register_msgs = {
    "name": ms.enter_name_message,
    "surname": ms.enter_surname_message,
    "phone": "Поділіться вашим номером телефону, натиснувши кнопку внизу. Це необхідно для зворотнього зв'язку з вами.",
}


class Registration(StatesGroup):
    name = State()
    surname = State()
    phone = State()


@register_router.message(StateFilter(Registration), F.command("cancel"))
@register_router.message(StateFilter(Registration), F.text.casefold() == "cancel")
async def register_cancel(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer("Процес реєстрації зупинено", reply_markup=make_wo_auth_kb())


@register_router.message(StateFilter(Registration), F.command("back"))
@register_router.message(StateFilter(Registration), F.text.casefold() == "back")
async def register_back(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == Registration.name:
        await message.answer(
            "Не можливо повернутися на попредній крок, так як це перший. Для виходу натисніть кнопку 'Cancel'\n\n"
            + register_msgs["name"],
            reply_markup=make_cancel_kb(),
        )
        return

    previous = None
    for state_step in Registration.__all_states__:
        if state_step == current_state:
            await state.set_state(previous)
            break

        previous = state_step

    if previous == Registration.phone:
        reply_markup = make_share_contact_kb()
    else:
        reply_markup = make_cancel_kb()

    await message.answer(
        register_msgs[previous.state.split(":")[-1]],
        reply_markup=reply_markup,
    )


@register_router.message(F.text.lower() == "register")
async def start_registration(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Registration.name)
    await message.answer(ms.enter_name_message, reply_markup=make_cancel_kb())


@register_router.message(Registration.name, F.text)
async def registration_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if not validate_name(name):
        await message.answer(ms.invalid_name_message)
        return

    await state.update_data(name=name)
    await state.set_state(Registration.surname)
    await message.answer(ms.enter_surname_message, reply_markup=make_cancel_kb())


@register_router.message(Registration.surname, F.text)
async def registration_surname(message: Message, state: FSMContext):
    surname = message.text.strip()
    if not validate_name(surname):
        await message.answer(ms.invalid_name_message)
        return

    await state.update_data(surname=surname)
    await state.set_state(Registration.phone)
    await message.answer(
        "Поділіться вашим номером телефону, натиснувши кнопку внизу. Це необхідно для зворотнього зв'язку з вами.",
        reply_markup=make_share_contact_kb(),
    )


@register_router.message(Registration.phone, F.contact | F.text)
async def registration_phone(
    message: Message, state: FSMContext, session: AsyncSession
):
    if message.contact:
        phone = message.contact.phone_number
        if not phone.startswith("+"):
            phone = "+" + phone

        await state.update_data(phone=phone)
    else:
        if is_valid_number(message.text):
            await state.update_data(phone=message.text)
        else:
            await message.answer(
                'Не корректний номер телефону. Якщо вводите "руками", то пишіть повний формат номеру,'
                'наприклад: "+380991234567". А краще скористайтеся кнопкою внизу: "Поділитися контактом"'
            )
            return

    data = await state.get_data()
    user = UserCreate(
        name=data["name"],
        surname=data["surname"],
        phone_number=data["phone"],
        username=message.from_user.username,
        user_id=message.from_user.id,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    try:
        await crud.create_user(session=session, user=user)
        logger.info(f"[DB] User {user.name} {user.surname} ({message.from_user.id}) is registered")

        await message.answer(
            f"Дякуємо за реєстрацію, {data['name']}!", reply_markup=make_user_kb()
        )
    except IntegrityError:
        logger.error(
            f"[DB] registration error: User {message.from_user} is already registered"
        )
        await message.answer("Ви вже зареєстровані", reply_markup=make_user_kb())
    except Exception as e:
        logger.error(
            f"[GENERAL] registration error: {e}. Failed to register user: {message.from_user}"
        )
        await message.answer(f"Помилка реєстрації, {ms.reload_help_message}")
    finally:
        await state.clear()
