import json
import logging
from datetime import datetime, timedelta

from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, get_user_locale
from db_handler import crud
from db_handler.models import Order, OrderItemAssociation
from filters import TextOrCommand
from keyboards.keyboard import (
    make_cancel_kb,
    make_user_kb,
    make_web_app_kb,
    make_wo_auth_kb,
)
from services import process_order_submission
from services.notification_service import (
    build_user_confirmation_message,
    notify_admin_new_order,
)
from utils import messages as ms
from utils import utils

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
            await bot.delete_message(chat_id=chat_id, message_id=data["last_msg_id"])
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")


def construct_calendar(locale: str):
    today = datetime.today()
    calendar = SimpleCalendar(locale=locale, show_alerts=True)
    calendar.set_dates_range(datetime(today.year, today.month, today.day), today + timedelta(days=365))
    return calendar


class OrderStates(StatesGroup):
    date_start = State()
    date_end = State()
    work_days = State()
    address = State()
    comment = State()
    items = State()


@order_router.callback_query(StateFilter(None), F.data.startswith("edit_order"))
async def order_edit(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession):
    logger.info(f'start order editing, callback_query= {callback_query.data}')
    await state.clear()

    order_orm = await crud.get_order_with_items(
        session=session,
        order_id=int(callback_query.data.split("_")[2]),
    )
    logger.info(order_orm)
    
    if not order_orm:
        await callback_query.answer("Замовлення не знайдено", show_alert=True)
        await state.clear()
        return 
    
    await callback_query.message.answer(
        "Починаємо редагування замовлення, для пропуску кроку введіть . (крапку)", reply_markup=make_cancel_kb()
    )
    await state.set_state(OrderStates.date_start)
    await state.update_data(order_id_for_edit=order_orm.id)
    calendar = construct_calendar(await get_user_locale(callback_query.from_user))
    msg = await callback_query.message.answer(
        order_msgs["date_start"],
        reply_markup=await calendar.start_calendar(),
    )
    await state.update_data(last_msg_id=msg.message_id)


@order_router.message(TextOrCommand("order"))
async def order_start(message: Message, state: FSMContext, session: AsyncSession):
    user = await crud.get_user_by_tg_id(session=session, user_id=message.from_user.id)
    if not user:
        await message.answer(
            ms.not_authorized_message,
            reply_markup=make_wo_auth_kb(),
        )
        logger.warning(f"[ORDER] User {message.from_user.id} is not authorized")
        return

    await state.clear()
    await state.set_state(OrderStates.date_start)
    await message.answer(
        "Починаємо оформлення замовлення", reply_markup=make_cancel_kb()
    )
    calendar = construct_calendar(await get_user_locale(message.from_user))
    msg = await message.answer(
        order_msgs["date_start"],
        reply_markup=await calendar.start_calendar(),
    )
    await state.update_data(last_msg_id=msg.message_id)


@order_router.message(OrderStates.date_start, F.text == ".")
async def edit_date_start(message: Message, state: FSMContext, session: AsyncSession):
    calendar = construct_calendar(await get_user_locale(message.from_user))
    data = await state.get_data()
    order_id = data.get("order_id_for_edit")
    
    if order_id is None:
        text = "Дату початку ще не обрано. Оберіть дату початку"
    else:
        order_orm = await crud.get_order_with_items(session, order_id)
        if order_orm:
            text = order_msgs["date_end"]
            await state.update_data(date_start=order_orm.date_start)
            await state.set_state(OrderStates.date_end)
        else:
            text = "Замовлення для редагування не знайдено. Оберіть дату початку"

    msg = await message.answer(
        text,
        reply_markup=await calendar.start_calendar(),
    )
    await state.update_data(last_msg_id=msg.message_id)


@order_router.message(OrderStates.date_end, F.text == ".")
async def edit_date_end(message: Message, state: FSMContext, session: AsyncSession):
    calendar = construct_calendar(await get_user_locale(message.from_user))
    data = await state.get_data()
    order_id = data.get("order_id_for_edit")

    if order_id is None:
        msg = await message.answer(
            "Дату повернення ще не обрано. Оберіть дату повернення",
            reply_markup=await calendar.start_calendar(),
        )
        await state.update_data(last_msg_id=msg.message_id)
        return 

    order_orm = await crud.get_order_with_items(session, order_id)
    if not order_orm:
        await message.answer("Замовлення для редагування не знайдено")
        return

    await state.update_data(date_end=order_orm.date_end)
    await state.set_state(OrderStates.work_days)

    msg = await message.answer(order_msgs["work_days"])
    await state.update_data(last_msg_id=msg.message_id)


@order_router.callback_query(OrderStates.date_start, SimpleCalendarCallback.filter())
async def process_date_start_calendar(
    callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext
):
    calendar = construct_calendar(await get_user_locale(callback_query.from_user))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await state.update_data(date_start=date)
        await state.set_state(OrderStates.date_end)
        await callback_query.message.edit_text(
            f"Дата отримання обладнання: {date.strftime('%d.%m.%Y')}"
        )

        msg = await callback_query.message.answer(
            order_msgs["date_end"],
            reply_markup=await calendar.start_calendar(),
        )
        await state.update_data(last_msg_id=msg.message_id)


@order_router.callback_query(OrderStates.date_end, SimpleCalendarCallback.filter())
async def process_date_end_calendar(
    callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext
):
    calendar = construct_calendar(await get_user_locale(callback_query.from_user))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await state.update_data(date_end=date)
        await state.set_state(OrderStates.work_days)
        await callback_query.message.edit_text(
            f"Дата повернення обладнання: {date.strftime('%d.%m.%Y')}"
        )
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
    await message.answer("Процес замовлення зупинено", reply_markup=make_user_kb())


@order_router.message(StateFilter(OrderStates), F.command("back"))
@order_router.message(StateFilter(OrderStates), F.text.casefold() == "back")
async def order_back(message: Message, state: FSMContext):
    current_state = await state.get_state()
    await message.delete()
    calendar = construct_calendar(await get_user_locale(message.from_user))
    if current_state == OrderStates.date_start:
        answer_text = "Не можливо повернутися на попредній крок, так як це перший. Для виходу натисніть кнопку 'Cancel'\n\n"
        answer_text += order_msgs["date_start"]
        msg = await message.answer(
            answer_text,
            reply_markup=await calendar.start_calendar(),
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
            reply_markup=await calendar.start_calendar(),
        )
        await delete_last_msg(bot=message.bot, chat_id=message.chat.id, state=state)
        await state.update_data(last_msg_id=msg.message_id)
        return

    await message.answer(
        order_msgs[previous.state.split(":")[-1]],
        reply_markup=make_cancel_kb(),
    )


@order_router.message(OrderStates.work_days, F.text)
async def order_work_days(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    order_id = data.get("order_id_for_edit")

    if message.text == '.':
        if order_id is None:
            await message.answer(ms.not_in_edit_mode_message + order_msgs["work_days"])
            return

        order_orm = await crud.get_order_with_items(session, order_id)
        if not order_orm:
            await message.answer("Замовлення для редагування не знайдено")
            return
        work_days = order_orm.work_days
    else:
        work_days = utils.work_days_validation(message.text)

    await state.set_state(OrderStates.address)
    if work_days:
        if work_days > 365: # todo: get rid of this check
            await state.clear()
            await message.answer(
                "Здається ви плануєте оренду більше 365 днів. Зв’яжіться з менеджером напряму",
                reply_markup=make_user_kb(),
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
async def order_address(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    order_id = data.get("order_id_for_edit")

    if message.text == '.':
        if order_id is None:
            await message.answer(ms.not_in_edit_mode_message + order_msgs["address"])
            return

        order_orm = await crud.get_order_with_items(session, order_id)
        if not order_orm:
            await message.answer("Замовлення для редагування не знайдено")
            return
        address = order_orm.address
    else:
        address = message.text

    await state.set_state(OrderStates.comment)
    await state.update_data(address=address)
    await message.answer(order_msgs["comment"])


@order_router.message(OrderStates.address)
async def order_address_bad_input(message: Message, state: FSMContext):
    await message.answer(ms.bad_input_message + "\n\n" + order_msgs["address"])


@order_router.message(OrderStates.comment, F.text)
async def order_comment(message: Message, state: FSMContext, session: AsyncSession):
    items = None 
    data = await state.get_data()
    order_id = data.get("order_id_for_edit")

    if order_id:
        order_orm = await crud.get_order_with_items(session, order_id)
        if order_orm:
            items = order_orm.items_details
    
    if message.text == '.':
        if order_id is None:
            await message.answer(ms.not_in_edit_mode_message + order_msgs["comment"])
            return

        if not order_orm:
             await message.answer("Замовлення для редагування не знайдено")
             return
        comment = order_orm.description
        
    else:
        comment = message.text

    
    await state.set_state(OrderStates.items)
    await state.update_data(comment=comment)
    
    kb = make_web_app_kb(work_days=data["work_days"], items=items)
    logger.info(f"Send items to web app = {items}")
    await message.answer(order_msgs["items"], reply_markup=kb)


@order_router.message(OrderStates.comment)
async def order_comment_bad_input(message: Message, state: FSMContext):
    await message.answer(ms.bad_input_message + "\n\n" + order_msgs["comment"])


@order_router.message(OrderStates.items, F.web_app_data)
async def order_final(message: Message, state: FSMContext, session: AsyncSession):
    """Process order data sent from the Web App."""
    user_reply_message = ms.failed_to_send_order_message

    try:
        state_data = await state.get_data()
        web_app_data = json.loads(message.web_app_data.data)
        items = web_app_data.get("items", [])
        if not items:
            await message.answer("Ви не вибрали жодної позиції обладнання", reply_markup=make_user_kb())
            await state.clear()
            return

        order_id = state_data.get("order_id_for_edit")
        order_for_edit = None
        if order_id:
            order_for_edit = await crud.get_order_with_items(session, order_id)

        user = await crud.get_user_by_tg_id(session=session, user_id=message.from_user.id)
        order = await process_order_submission(
            user=user,
            state_data=state_data,
            items=items,
            order_for_edit=order_for_edit,
            session=session,
        )

        order_with_items = await crud.get_order_with_items(
            session=session, order_id=order.id
        )
        was_edited = bool(order_for_edit)
        await notify_admin_new_order(
            bot=message.bot,
            order=order_with_items,
            user=user,
            was_edited=was_edited,
        )
        user_reply_message = build_user_confirmation_message(
            order_with_items,
            was_edited=was_edited,
        )
        logger.info(user_reply_message)

    except json.JSONDecodeError:
        user_reply_message = ms.failed_to_send_order_message
        logger.error(f"Invalid JSON from web app: {message.web_app_data.data}")

    except Exception as e:
        user_reply_message = ms.failed_to_send_order_message
        logger.error(f"Error handling web app data: {e}")

    finally:
        await state.clear()
        await message.answer(user_reply_message, reply_markup=make_user_kb())



@order_router.message(OrderStates.items)
async def order_items_bad_input(message: Message, state: FSMContext):
    await message.answer("Не вірні дані\n\n" + order_msgs["items"])
