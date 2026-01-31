import json
import logging
from datetime import datetime

from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, get_user_locale
from config import settings
from db_handler import crud
from db_handler.crud import get_user_by_tg_id
from db_handler.schemas.order import OrderCreate
from filters import TextOrCommand
from keyboards.inline import make_admin_order_inline_kb
from keyboards.keyboard import (
    make_auth_kb,
    make_order_cancel_kb,
    make_web_app_kb,
    make_wo_auth_kb,
)
from utils import messages as ms
from utils import utils
from utils.order_msg_builder import OrderAdminMsgBuilder, OrderUserMsgBuilder

order_router = Router()


logger = logging.getLogger(__name__)


order_msgs = {
    "date_start": "Оберіть дату отримання обладнання",
    "date_end": "Оберіть дату повернення обладнання",
    "work_days": "Введіть кількість днів роботи одним числом, наприклад: 3",
    "address": "Введіть адресу та час доставки\nАбо час самовивозу зі складу (м. Київ, Здолбунівська 2)",
    "comment": "Введіть коментар до замовлення",
    "items": "Оберіть з каталогу обладнання, натиснувши на кнопку знизу",
}


async def delete_last_msg(bot: Bot, chat_id: int, state: FSMContext):
    data = await state.get_data()
    if data.get("last_msg_id"):
        try:
            await bot.delete_message(
                chat_id=chat_id, message_id=data["last_msg_id"]
            )
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")


class OrderStates(StatesGroup):
    date_start = State()
    date_end = State()
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
    await state.set_state(OrderStates.date_start)
    await message.answer("Починаємо оформлення замовлення", reply_markup=make_order_cancel_kb())
    msg = await message.answer(
        order_msgs["date_start"],
        reply_markup=await SimpleCalendar(
            locale=await get_user_locale(message.from_user)
        ).start_calendar(),
    )
    await state.update_data(last_msg_id=msg.message_id)


@order_router.callback_query(OrderStates.date_start, SimpleCalendarCallback.filter())
async def process_date_start_calendar(
    callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext
):
    calendar = SimpleCalendar(
        locale=await get_user_locale(callback_query.from_user), show_alerts=True
    )
    calendar.set_dates_range(datetime(2026, 1, 1), datetime(2027, 12, 31)) #todo: make dates dynamic
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await state.update_data(date_start=date)
        await state.set_state(OrderStates.date_end)
        await callback_query.message.edit_text(f"Дата отримання обладнання: {date.strftime('%d.%m.%Y')}")
        msg = await callback_query.message.answer(
            order_msgs["date_end"],
            reply_markup=await SimpleCalendar(
                locale=await get_user_locale(callback_query.from_user)
            ).start_calendar(),
        )
        await state.update_data(last_msg_id=msg.message_id)


@order_router.callback_query(OrderStates.date_end, SimpleCalendarCallback.filter())
async def process_date_end_calendar(
    callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext
):
    calendar = SimpleCalendar(
        locale=await get_user_locale(callback_query.from_user), show_alerts=True
    )
    calendar.set_dates_range(datetime(2026, 1, 1), datetime(2027, 12, 31)) #todo: make dates dynamic
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await state.update_data(date_end=date)
        await state.set_state(OrderStates.work_days)
        await callback_query.message.edit_text(f"Дата повернення обладнання: {date.strftime('%d.%m.%Y')}")
        msg = await callback_query.message.answer(
            order_msgs["work_days"],
        )
        await state.update_data(last_msg_id=msg.message_id)


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
    await message.delete()
    calendar_kb = await SimpleCalendar(locale=await get_user_locale(message.from_user)).start_calendar()
    if current_state == OrderStates.date_start:
        answer_text = "Не можливо повернутися на попредній крок, так як це перший. Для виходу натисніть кнопку 'Cancel'\n\n"
        answer_text += order_msgs["date_start"]
        msg = await message.answer(
            answer_text,
            reply_markup=calendar_kb,
        )
        await delete_last_msg(bot=message.bot, chat_id=message.chat.id, state=state)
        await state.update_data(last_msg_id=msg.message_id)
        return

    previous = None
    for state_step in OrderStates.__all_states__:
        if state_step == current_state:
            await state.set_state(previous)
            break

        previous = state_step
    
    if previous == OrderStates.date_end or previous == OrderStates.date_start:
        msg = await message.answer(
            order_msgs[previous.state.split(":")[-1]],
            reply_markup=calendar_kb,
        )
        await delete_last_msg(bot=message.bot, chat_id=message.chat.id, state=state)
        await state.update_data(last_msg_id=msg.message_id)
        return

    await message.answer(
        order_msgs[previous.state.split(":")[-1]],
        reply_markup=make_order_cancel_kb(),
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
        if not items:
            user_reply_message = "Ви не вибрали жодного товару"
            return

        user = await get_user_by_tg_id(session=session, user_id=message.from_user.id)
        order_dto = OrderCreate(
            user_id=user.user_id,
            date_start=state_data["date_start"],
            date_end=state_data["date_end"],
            work_days=state_data["work_days"],
            address=state_data["address"],
            description=state_data["comment"],
        )
        order = await crud.create_order_with_items(
            session=session, order=order_dto, items=items
        )
        order_with_items = await crud.get_order_with_items(
            session=session, order_id=order.id
        )

        logger.info(f"[ORDER] ORDER FROM {message.from_user.id} created: {order_dto}")
        order_text = OrderAdminMsgBuilder(
            order=order_with_items,
            items=order_with_items.items_details,
            user=user,
        ).build_full_message()

        await message.bot.send_message(
            chat_id=settings.telegram.manager_id,
            text=order_text,
            reply_markup=make_admin_order_inline_kb(
                order_id=order.id, status=order.status
            ),
        )

        user_reply_message = (
            ms.order_processing_message
            + ". Менеджер зв'яжеться з вами для підтвердження\n\n"
            + OrderUserMsgBuilder(
                order=order_with_items,
                items=order_with_items.items_details,
            ).build_full_message()
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
    await message.answer("Не вірні дані\n\n" + order_msgs["items"])
