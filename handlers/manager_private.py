from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from aiogram_calendar import (
    DialogCalendar,
    ManagerCalendarCallback,
    get_user_locale,
)
from config import settings
from db_handler import OrderStatus, crud
from filters.custom import IsManager
from keyboards import make_admin_order_inline_kb, make_user_order_inline_kb
from utils.order_msg_builder import OrderMsgBuilderFactory
from utils.utils import create_orders_count_dict

manager_router = Router()
manager_router.message.filter(IsManager())
manager_router.callback_query.filter(IsManager())


async def orders_with_status_list(
    message: Message, session: AsyncSession, status: OrderStatus
):
    orders = await crud.get_orders_with_status(session=session, status=status)

    if not orders:
        await message.answer(f"Немає замовлень, зі статусом: {status}")
        return

    await message.answer(
        "Оберіть місяць: ",
        reply_markup=await DialogCalendar(locale=await get_user_locale(message.from_user), status=status).start_calendar(),
    )

@manager_router.callback_query(ManagerCalendarCallback.filter())
async def process_order_calendar_manager(
    callback_query: CallbackQuery,
    callback_data: ManagerCalendarCallback,
    session: AsyncSession,
):
    orders = await crud.get_orders_with_status(
        session=session, status=callback_data.status
    )

    selected, date = await DialogCalendar(
        locale=await get_user_locale(callback_query.from_user),
        orders_count_dict=create_orders_count_dict(orders),
        status=callback_data.status,
    ).process_selection(callback_query, callback_data)
    if not selected:
        return

    orders_for_month = await crud.get_orders_with_status_and_date_start(
        session=session,
        status=callback_data.status,
        date=date,
    )
    if not orders_for_month:
        await callback_query.message.answer(f"Замовлень за {date.strftime('%m/%Y')} не знайдено.")
        await callback_query.message.delete()
        return

    for order in orders_for_month:
        await callback_query.message.answer(
            OrderMsgBuilderFactory.get_builder(
                order=order,
                items=order.items_details,
                user=order.user,
            ).build_preview_message(),
            reply_markup=make_admin_order_inline_kb(
                order_id=order.id,
                status=callback_data.status,
            ),
        )
    await callback_query.message.delete()


@manager_router.message(Command("active_orders"))
async def active_orders_list(message: Message, session: AsyncSession):
    await orders_with_status_list(
        message=message, session=session, status=OrderStatus.ACTIVE
    )


@manager_router.message(Command("pending_orders"))
async def pending_orders_list(message: Message, session: AsyncSession):
    await orders_with_status_list(
        message=message, session=session, status=OrderStatus.PENDING
    )


@manager_router.message(Command("completed_orders"))
async def completed_orders_list(message: Message, session: AsyncSession):
    await orders_with_status_list(
        message=message, session=session, status=OrderStatus.COMPLETED
    )


@manager_router.message(Command("cancelled_orders"))
async def cancelled_orders_list(message: Message, session: AsyncSession):
    await orders_with_status_list(
        message=message, session=session, status=OrderStatus.CANCELLED
    )


async def change_order_status(
    callback_query: CallbackQuery, session: AsyncSession, status: OrderStatus
):
    order_id = int(callback_query.data.split("_")[-1])
    order = await crud.get_order_by_id(session=session, order_id=order_id)
    if order is None:
        await callback_query.answer("Замовлення не знайдено", show_alert=True)
        return

    order.status = status
    await session.commit()

    new_keyboard = make_admin_order_inline_kb(order_id=order.id, status=status)
    new_msg_text = OrderMsgBuilderFactory.get_builder(
        order=order,
        items=[],
        user=order.user,
    ).build_full_message()

    order_status_text = f"Статус замовлення #{order_id} змінено на {status.value}"
    await callback_query.message.edit_text(text=new_msg_text, reply_markup=new_keyboard)
    await callback_query.answer(order_status_text)

    user_notification_text = order_status_text + "\n\n"

    await callback_query.message.bot.send_message(
        chat_id=order.user.user_id,
        text=user_notification_text,
        reply_markup=make_user_order_inline_kb(order_id=order.id, status=status),
        disable_notification=settings.telegram.disable_notification,
    )


@manager_router.callback_query(F.data.startswith("confirm_order"))
async def confirm_order(callback_query: CallbackQuery, session: AsyncSession):
    await change_order_status(
        callback_query=callback_query,
        session=session,
        status=OrderStatus.ACTIVE,
    )


@manager_router.callback_query(F.data.startswith("cancel_order"))
async def cancel_order(callback_query: CallbackQuery, session: AsyncSession):
    await change_order_status(
        callback_query=callback_query,
        session=session,
        status=OrderStatus.CANCELLED,
    )


@manager_router.callback_query(F.data.startswith("delete_order"))
async def delete_order(callback_query: CallbackQuery, session: AsyncSession):
    await callback_query.answer("Видалення поки що не підтримується")
