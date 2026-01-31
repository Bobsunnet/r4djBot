import enum

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from aiogram_calendar import (
    DialogCalendar,
    ManagerCalendarCallback,
    get_user_locale,
)
from config import settings
from db_handler import OrderStatus, crud
from filters.custom import IsManager
from keyboards import (
    OrderAction,
    OrderCallbackData,
    make_admin_order_inline_kb,
    make_user_order_inline_kb,
)
from utils.order_msg_builder import OrderAdminMsgBuilder
from utils.utils import create_orders_count_dict

manager_router = Router()
manager_router.message.filter(IsManager())
manager_router.callback_query.filter(IsManager())


class ConfirmationEnum(enum.Enum):
    YES = 'yes'
    NO = 'no'


class DeleteOrderCallbackData(CallbackData, prefix="delete_order"):
    order_id: int
    confirmation: ConfirmationEnum
    status: OrderStatus


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
            OrderAdminMsgBuilder(
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
    callback_query: CallbackQuery, callback_data: OrderCallbackData, session: AsyncSession, status: OrderStatus
):
    order_id = callback_data.order_id
    order = await crud.get_order_by_id(session=session, order_id=order_id)
    if order is None:
        await callback_query.answer("Замовлення не знайдено", show_alert=True)
        return

    order.status = status
    await session.commit()

    new_keyboard = make_admin_order_inline_kb(order_id=order.id, status=status)
    new_msg_text = OrderAdminMsgBuilder(
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


@manager_router.callback_query(OrderCallbackData.filter(F.action == OrderAction.CONFIRM))
async def confirm_order(callback_query: CallbackQuery, callback_data: OrderCallbackData, session: AsyncSession):
    await change_order_status(
        callback_query=callback_query,
        callback_data=callback_data,
        session=session,
        status=OrderStatus.ACTIVE,
    )


@manager_router.callback_query(OrderCallbackData.filter(F.action == OrderAction.CANCEL))
async def cancel_order(callback_query: CallbackQuery, callback_data: OrderCallbackData, session: AsyncSession):
    await change_order_status(
        callback_query=callback_query,
        callback_data=callback_data,
        session=session,
        status=OrderStatus.CANCELLED,
    )


@manager_router.callback_query(DeleteOrderCallbackData.filter(F.confirmation == ConfirmationEnum.YES))
async def confirm_delete_order(callback_query: CallbackQuery, callback_data: DeleteOrderCallbackData, session: AsyncSession):
    order_id = callback_data.order_id
    order = await crud.get_order_by_id(session=session, order_id=order_id)
    if order is None:
        await callback_query.answer("Замовлення не знайдено", show_alert=True)
        return
    
    await crud.delete_order(session=session, order_id=order_id)
    await callback_query.answer("Замовлення видалено", show_alert=True)
    await callback_query.message.delete()


@manager_router.callback_query(DeleteOrderCallbackData.filter(F.confirmation == ConfirmationEnum.NO))
async def cancel_delete_order(callback_query: CallbackQuery, callback_data: DeleteOrderCallbackData, session: AsyncSession):
    order_id = callback_data.order_id
    order = await crud.get_order_by_id(session=session, order_id=order_id)
    if order is None:
        await callback_query.answer("Замовлення не знайдено", show_alert=True)
        return
    
    new_msg_text = OrderAdminMsgBuilder(
        order=order,
        items=[],
        user=order.user,
    ).build_full_message()
    
    kb = make_admin_order_inline_kb(order_id=order_id, status=callback_data.status)
    await callback_query.message.edit_text(text=new_msg_text, reply_markup=kb)


@manager_router.callback_query(OrderCallbackData.filter(F.action == OrderAction.DELETE))
async def delete_order(callback_query: CallbackQuery, callback_data: OrderCallbackData, session: AsyncSession):
    order_id = callback_data.order_id
    # old_msg = callback_query.message.text
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="Так, видалити",
            callback_data=DeleteOrderCallbackData(
                order_id=order_id,
                status=OrderStatus.CANCELLED,
                confirmation=ConfirmationEnum.YES,
            ).pack(),
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="Ні, скасувати",
            callback_data=DeleteOrderCallbackData(
                order_id=order_id,
                status=OrderStatus.CANCELLED,
                confirmation=ConfirmationEnum.NO,
            ).pack(),
        )
    )
    await callback_query.message.edit_text(f"Ви впевнені, що хочете видалити замовлення #{order_id} ?", reply_markup=builder.as_markup())
