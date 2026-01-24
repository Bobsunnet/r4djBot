import json
import logging

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from db_handler import crud
from db_handler.crud import get_user_by_tg_id
from db_handler.schemas.order import OrderCreate
from filters import TextOrCommand
from keyboards.keyboard import (
    make_auth_kb,
    make_order_cancel_kb,
    make_web_app_kb,
    make_wo_auth_kb,
)
from utils import messages as ms
from utils import utils

order_router = Router()

logger = logging.getLogger(__name__)


order_msgs = {
    "date": f"Введіть дати отримання і повернення обладнання у форматі:{ms.date_format_message}",
    "work_days": "Введіть кількість днів роботи одним числом, наприклад: 3",
    "address": "Введіть адресу та час доставки\nАбо час самовивозу зі складу (м. Київ, Здолбунівська 2)",
    "comment": "Введіть коментар до замовлення",
    "items": "Оберіть з каталогу обладнання, натиснувши на кнопку знизу",
}


class OrderStates(StatesGroup):
    date = State()
    work_days = State()
    address = State()
    comment = State()
    items = State()


@order_router.message(TextOrCommand("order"))
async def order_start(message: Message, state: FSMContext, session: AsyncSession):
    user = await get_user_by_tg_id(session=session, user_id=message.from_user.id)
    if not user:
        await message.answer(
            ms.not_authorized_message,
            reply_markup=make_wo_auth_kb(),
        )
        return

    await state.clear()
    await state.set_state(OrderStates.date)
    await message.answer(
        order_msgs["date"],
        reply_markup=make_order_cancel_kb(),
    )


@order_router.message(StateFilter(OrderStates), F.command("cancel"))
@order_router.message(StateFilter(OrderStates), F.text.casefold() == "cancel")
async def order_cancel(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer("Процес замовлення зупинено", reply_markup=make_auth_kb())


@order_router.message(StateFilter(OrderStates), F.command("back"))
@order_router.message(StateFilter(OrderStates), F.text.casefold() == "back")
async def order_back(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state == OrderStates.date:
        await message.answer(
            "Не можливо повернутися на попредній крок, так як це перший. Для виходу натисніть кнопку 'Cancel'"
            + "\n\n"
            + order_msgs["date"]
        )
        return

    previous = None
    for state_step in OrderStates.__all_states__:
        if state_step == current_state:
            await state.set_state(previous)
            await message.answer(
                order_msgs[previous.state.split(":")[-1]],
                reply_markup=make_order_cancel_kb(),
            )
            return

        previous = state_step


@order_router.message(OrderStates.date, F.text)
async def order_date(message: Message, state: FSMContext):
    await state.set_state(OrderStates.work_days)

    try:
        start_date, end_date = utils.extract_date(message.text)
        start_date = utils.validate_date(start_date)
        end_date = utils.validate_date(end_date)

        if not start_date or not end_date:
            await state.set_state(OrderStates.date)
            await message.answer(
                f"Вказано неіснуючу дату. Введіть дати у форматі:{ms.date_format_message}"
            )
            return

        await state.update_data({"start_date": start_date, "end_date": end_date})
        await message.answer(order_msgs["work_days"])

    except ValueError:
        await state.set_state(OrderStates.date)
        await message.answer(
            f"Невірний формат дати. Введіть дати у форматі:{ms.date_format_message}"
        )


@order_router.message(OrderStates.date)
async def order_date_bad_input(message: Message, state: FSMContext):
    await message.answer(ms.bad_input_message + "\n\n" + order_msgs["date"])


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
        await message.answer(order_msgs["address"])

    else:
        await state.set_state(OrderStates.work_days)
        await message.answer(
            "Невірний формат кількості. Введіть кількість днів роботи одним числом, наприклад: 3"
        )


@order_router.message(OrderStates.work_days)
async def order_work_days_bad_input(message: Message, state: FSMContext):
    await message.answer(ms.bad_input_message + "\n\n" + order_msgs["work_days"])


@order_router.message(OrderStates.address, F.text)
async def order_address(message: Message, state: FSMContext):
    await state.set_state(OrderStates.comment)
    await state.update_data(address=message.text)
    await message.answer(order_msgs["comment"])


@order_router.message(OrderStates.address)
async def order_address_bad_input(message: Message, state: FSMContext):
    await message.answer(ms.bad_input_message + "\n\n" + order_msgs["address"])


@order_router.message(OrderStates.comment, F.text)
async def order_comment(message: Message, state: FSMContext):
    await state.set_state(OrderStates.items)
    await state.update_data(comment=message.text)
    data = await state.get_data()

    await message.answer(
        order_msgs["items"],
        reply_markup=make_web_app_kb(data["work_days"]),
    )


@order_router.message(OrderStates.comment)
async def order_comment_bad_input(message: Message, state: FSMContext):
    await message.answer(ms.bad_input_message + "\n\n" + order_msgs["comment"])


@order_router.message(OrderStates.items, F.web_app_data)
async def order_final(message: Message, state: FSMContext, session: AsyncSession):
    """Process order data sent from the Web App."""

    try:
        state_data = await state.get_data()
        web_app_data = json.loads(message.web_app_data.data)
        items = web_app_data.get("items", [])
        logger.info(
            f"[ORDER] ORDER request FROM {message.from_user.id} received: {items}"
        )
        if not items:
            user_reply_message = "Ви не вибрали жодного товару"
            return

        user = await get_user_by_tg_id(session=session, user_id=message.from_user.id)
        order = OrderCreate(
            user_id=user.id,
            date_start=state_data["start_date"],
            date_end=state_data["end_date"],
            work_days=state_data["work_days"],
            address=state_data["address"],
            description=state_data["comment"],
        )

        order = await crud.create_order(session=session, order=order)
        logger.info(f"[ORDER] ORDER FROM {message.from_user.id} created: {order}")
        order_text = utils.format_order_message_for_admin(
            user=user,
            order=order,
            items=items,
        )

        try:
            await message.bot.send_message(
                chat_id=settings.telegram.manager_id, text=order_text
            )
            user_reply_message = (
                ms.order_processing_message
                + ". Менеджер зв'яжеться з вами для підтвердження\n"
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

    except Exception as e:
        user_reply_message = ms.failed_to_send_order_message
        logger.error(f"Error handling web app data: {e}")

    finally:
        await state.clear()
        await message.answer(user_reply_message, reply_markup=make_auth_kb())


@order_router.message(OrderStates.items)
async def order_items_bad_input(message: Message, state: FSMContext):
    await message.answer(ms.bad_input_message + "\n\n" + order_msgs["items"])
