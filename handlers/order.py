import json
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

import config
from exceptions import exceptions
from filters import TextOrCommand
from keyboards.keyboard import make_auth_kb, make_web_app_kb, make_wo_auth_kb
from utils import messages as ms
from utils import utils
from utils.db_utils import get_authorized_user, get_user_phone_number

order_router = Router()
logger = logging.getLogger(__name__)


class OrderStates(StatesGroup):
    date = State()
    work_days = State()
    address = State()
    items = State()
    comment = State()


@order_router.message(TextOrCommand("order"))
async def order_start(message: Message, state: FSMContext):
    user = get_authorized_user(message.from_user.id)
    if not user:
        await message.answer(
            ms.not_authorized_message,
            reply_markup=make_wo_auth_kb(),
        )
        return
    await state.clear()
    await state.set_state(OrderStates.date)
    await message.answer(
        f"Введіть дати отримання і повернення обладнання у форматі:{ms.date_format_message}"
    )


@order_router.message(OrderStates.date, F.text)
async def order_date(message: Message, state: FSMContext):
    await state.set_state(OrderStates.work_days)
    try:
        start_date, end_date = utils.extract_date(message.text)
        if not utils.validate_date(start_date) or not utils.validate_date(end_date):
            await state.set_state(OrderStates.date)
            await message.answer(
                f"Вказано неіснуючу дату. Введіть дати у форматі:{ms.date_format_message}"
            )
            return

        await state.update_data({"start_date": start_date, "end_date": end_date})
        await message.answer("Введіть кількість днів роботи одним числом, наприклад: 3")
    except ValueError:
        await state.set_state(OrderStates.date)
        await message.answer(
            f"Невірний формат дати. Введіть дати у форматі:{ms.date_format_message}"
        )


@order_router.message(OrderStates.work_days, F.text)
async def order_work_days(message: Message, state: FSMContext):
    await state.set_state(OrderStates.address)
    work_days = utils.work_days_validation(message.text)
    if work_days:
        if work_days > 365:
            await state.clear()
            await message.answer(
                "Здається ви плануєте оренду більше 365 днів. Зв’яжіться з менеджером напряму",
                reply_markup=make_auth_kb(),
            )
            return

        await state.update_data(work_days=work_days)
        await message.answer(
            "Введіть адресу та час доставки\nАбо час самовивозу зі складу (м. Київ, Здолбунівська 2)"
        )
    else:
        await state.set_state(OrderStates.work_days)
        await message.answer(
            "Невірний формат кількості. Введіть кількість днів роботи одним числом, наприклад: 3"
        )


@order_router.message(OrderStates.address, F.text)
async def order_address(message: Message, state: FSMContext):
    await state.set_state(OrderStates.comment)
    await state.update_data(address=message.text)
    await message.answer("Введіть коментар до замовлення")


@order_router.message(OrderStates.comment, F.text)
async def order_comment(message: Message, state: FSMContext):
    await state.set_state(OrderStates.items)
    await state.update_data(comment=message.text)
    data = await state.get_data()
    await message.answer(
        "Оберіть з каталогу обладнання, натиснувши на кнопку знизу",
        reply_markup=make_web_app_kb(data["work_days"]),
    )


@order_router.message(F.web_app_data, OrderStates.items)
async def order_final(message: Message, state: FSMContext):
    """Process order data sent from the Web App."""
    try:
        state_data = await state.get_data()
        logger.debug(f"State data: {state_data}")
        web_app_data = json.loads(message.web_app_data.data)
        items = web_app_data.get("items", [])
        logger.info(f"ORDER FROM {message.from_user.id} received: {items}")
        if not items:
            user_reply_message = "Ви не вибрали жодного товару"
            return
        phone_number = get_user_phone_number(message.from_user.id)

        # Format order message
        order_text = utils.format_order_message(
            start_date=state_data["start_date"],
            end_date=state_data["end_date"],
            count=state_data["work_days"],
            address=state_data["address"],
            comment=state_data["comment"],
            user_full_name=message.from_user.full_name,
            username=message.from_user.username,
            phone_number=phone_number,
            items=items,
        )

        try:
            await message.bot.send_message(chat_id=config.MANAGER_ID, text=order_text)
            user_reply_message = (
                ms.order_processing_message
                + "\n"
                + "\n".join(order_text.split("\n")[2:])
            )

            logger.info(f"Order from {message.from_user.id} sent to manager")
        except Exception as e:
            logger.error(f"Failed to send order to manager: {e}")
            user_reply_message = (
                ms.order_processing_message
                + " але не було надіслане менеджеру. Зверніться до менеджера."
            )

    except json.JSONDecodeError:
        user_reply_message = ms.failed_to_send_order_message
        logger.error(f"Invalid JSON from web app: {message.web_app_data.data}")
    except exceptions.UserNotFound:
        user_reply_message = ms.not_authorized_message + ms.failed_to_send_order_message
        logger.error(f"User not found in database: {message.from_user.id}")
    except Exception as e:
        user_reply_message = ms.failed_to_send_order_message
        logger.error(f"Error handling web app data: {e}")
    finally:
        await state.clear()
        await message.answer(user_reply_message, reply_markup=make_auth_kb())
