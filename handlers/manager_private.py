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


@manager_router.callback_query(F.data.startswith("confirm_order"))
async def confirm_order(callback_query: CallbackQuery, session: AsyncSession):
    order_id = int(callback_query.data.split("_")[-1])

    order = await crud.get_order_by_id(session=session, order_id=order_id)

    if order is None:
        await callback_query.message.answer("Замовлення не знайдено")
        return

    order.status = OrderStatus.ACTIVE

    await session.commit()

    await callback_query.message.answer(f"Замовлення {order_id} підтверджено")
