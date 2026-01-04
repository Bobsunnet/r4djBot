import json
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

import config
from db_handler.db_class import db_handler
from keyboards.keyboard import make_web_app_kb
from utils.utils import extract_date, format_order_message

order_router = Router()
logger = logging.getLogger(__name__)


failed_to_send_order_message = (
    f"Не вдалося обробити ваше замовлення. {config.reload_help_message}"
)


class UserNotFound(Exception):
    pass


class OrderStates(StatesGroup):
    date = State()
    count = State()
    address = State()
    items = State()


def get_user_phone_number(user_id: int) -> str:
    user = db_handler.read_user_by_user_id(user_id)
    if not user:
        raise UserNotFound("User not found in database")

    return user["phone_number"]


@order_router.message(F.text.lower() == "order")
async def order_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(OrderStates.date)
    await message.answer(
        "Введіть дати початку і кінця оренди у форматі:\ndd.mm.yy - dd.mm.yy"
    )


@order_router.message(OrderStates.date, F.text)
async def order_date(message: Message, state: FSMContext):
    await state.set_state(OrderStates.count)
    try:
        start_date, end_date = extract_date(message.text)
        await state.update_data({"start_date": start_date, "end_date": end_date})
        await message.answer("Введіть кількість днів роботи одним числом, наприклад: 3")
    except ValueError:
        await state.set_state(OrderStates.date)
        await message.answer(
            "Невірний формат дати. Введіть дати у форматі:\ndd.mm.yy - dd.mm.yy"
        )


@order_router.message(OrderStates.count, F.text)
async def order_count(message: Message, state: FSMContext):
    await state.set_state(OrderStates.address)
    try:
        count = int(message.text)
        await state.update_data(count=count)
        await message.answer("Введіть адресу доставки/самовивіз зі складу")
    except ValueError:
        await state.set_state(OrderStates.count)
        await message.answer(
            "Невірний формат кількості. Введіть кількість днів роботи одним числом, наприклад: 3"
        )


@order_router.message(OrderStates.address, F.text)
async def order_address(message: Message, state: FSMContext):
    await state.set_state(OrderStates.items)
    await state.update_data(address=message.text)
    await message.answer(
        "Оберіть з каталогу обладнання, натиснувши на кнопку знизу",
        reply_markup=make_web_app_kb(),
    )


@order_router.message(F.web_app_data, OrderStates.items)
async def order_final(message: Message, state: FSMContext):
    """Process order data sent from the Web App."""
    try:
        state_data = await state.get_data()
        logger.info(f"State data: {state_data}")

        web_app_data = json.loads(message.web_app_data.data)
        items = web_app_data.get("items", [])

        logger.info(f"ORDER FROM {message.from_user.id} received: {items}")

        if not items:
            await message.answer("Ваш кошик був порожнім. Немає замовлення.")
            return

        phone_number = get_user_phone_number(message.from_user.id)

        # Format order message
        order_text = format_order_message(
            start_date=state_data["start_date"],
            end_date=state_data["end_date"],
            count=state_data["count"],
            address=state_data["address"],
            user_full_name=message.from_user.full_name,
            username=message.from_user.username,
            phone_number=phone_number,
            items=items,
        )

        try:
            if config.DEBUG:
                logger.info(f"Order text:\n{order_text}")
            else:
                await message.bot.send_message(
                    chat_id=config.MANAGER_ID, text=order_text
                )
            await message.answer("✅ Замовлення прийнято!")
            if config.DEBUG:
                await message.answer(order_text)

            logger.info(f"Order from {message.from_user.id} sent to manager")
        except Exception as e:
            logger.error(f"Failed to send order to manager: {e}")
            await message.answer(
                "Замовлення прийнято, але не було надіслане менеджеру. "
                "Зверніться до менеджера."
            )

    except json.JSONDecodeError:
        await message.answer(failed_to_send_order_message)
        logger.error(f"Invalid JSON from web app: {message.web_app_data.data}")
    except Exception as e:
        await message.answer(failed_to_send_order_message)
        logger.error(f"Error handling web app data: {e}")
