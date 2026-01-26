from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from db_handler import OrderStatus, crud
from keyboards import make_admin_order_inline_kb
from utils import utils

manager_router = Router()


async def perform_order_list(
    message: Message, session: AsyncSession, status: OrderStatus
):
    if message.from_user.id != settings.telegram.manager_id:
        await message.answer("Ви не маєте доступу до цієї команди")
        return

    orders = await crud.get_orders_with_status(session=session, status=status)

    if not orders:
        await message.answer(f"Немає замовлень, зі статусом: {status}")
        return

    for order in orders:
        await message.answer(
            utils.format_order_message_for_admin(
                user=order.user, order=order, items=[]
            ),
            reply_markup=make_admin_order_inline_kb(order_id=order.id, status=status),
        )


@manager_router.message(Command("active_orders"))
async def active_orders_list(message: Message, session: AsyncSession):
    await perform_order_list(
        message=message, session=session, status=OrderStatus.ACTIVE
    )


@manager_router.message(Command("pending_orders"))
async def pending_orders_list(message: Message, session: AsyncSession):
    await perform_order_list(
        message=message, session=session, status=OrderStatus.PENDING
    )


@manager_router.message(Command("completed_orders"))
async def completed_orders_list(message: Message, session: AsyncSession):
    await perform_order_list(
        message=message, session=session, status=OrderStatus.COMPLETED
    )


@manager_router.message(Command("cancelled_orders"))
async def cancelled_orders_list(message: Message, session: AsyncSession):
    await perform_order_list(
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
    items_list = []

    new_keyboard = make_admin_order_inline_kb(order_id=order.id, status=status)
    new_msg_text = utils.format_order_message_for_admin(
        user=order.user, order=order, items=items_list
    )

    order_status_text = f"Статус замовлення #{order_id} змінено на {status.value}"
    await callback_query.message.edit_text(text=new_msg_text, reply_markup=new_keyboard)
    await callback_query.answer(order_status_text)

    user_notification_text = order_status_text + "\n\n"
    user_notification_text += utils.build_order_message_body(
        order=order, items=items_list
    )

    await callback_query.message.bot.send_message(
        chat_id=order.user.user_id,
        text=user_notification_text,
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


@manager_router.callback_query(F.data.startswith("show_details"))
async def show_order_details(callback_query: CallbackQuery, session: AsyncSession):
    order_id = int(callback_query.data.split("_")[-1])
    order = await crud.get_order_with_items(session=session, order_id=order_id)
    if order is None:
        await callback_query.answer("Замовлення не знайдено", show_alert=True)
        return

    items_list = []
    for item in order.items_details:
        items_list.append(
            {
                "name": item.item.name,
                "quantity": item.quantity,
            }
        )
    await callback_query.answer()
    await callback_query.message.edit_text(
        utils.format_order_message_for_admin(
            user=order.user,
            order=order,
            items=items_list,
        ),
        reply_markup=make_admin_order_inline_kb(order_id=order.id, status=order.status),
    )
