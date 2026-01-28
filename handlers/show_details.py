from contextlib import suppress

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from db_handler import crud
from db_handler.models import Order
from filters.custom import IsManager
from keyboards import make_admin_order_inline_kb, make_user_order_inline_kb
from utils.order_msg_builder import OrderMsgBuilderFactory

details_router = Router()


async def _get_order_or_answer(
    callback_query: CallbackQuery, session: AsyncSession
) -> Order | None:
    """Helper to fetch order or show 'not found' alert."""
    order_id = int(callback_query.data.split("_")[-1])
    order = await crud.get_order_with_items(session=session, order_id=order_id)
    if not order:
        await callback_query.answer("Замовлення не знайдено", show_alert=True)
        return None

    return order


@details_router.callback_query(F.data.startswith("show_details"), IsManager())
async def show_order_details_manager(
    callback_query: CallbackQuery, session: AsyncSession
):
    order = await _get_order_or_answer(callback_query, session)
    if order is None:
        return

    await callback_query.answer()
    with suppress(TelegramBadRequest):
        await callback_query.message.edit_text(
            OrderMsgBuilderFactory.get_builder(
                order=order,
                items=order.items_details,
                user=order.user,
            ).build_full_message(),
            reply_markup=make_admin_order_inline_kb(
                order_id=order.id, status=order.status
            ),
        )


@details_router.callback_query(F.data.startswith("show_details"))
async def show_order_details_user(callback_query: CallbackQuery, session: AsyncSession):
    order = await _get_order_or_answer(callback_query, session)
    if order is None:
        return

    await callback_query.answer(cache_time=10)
    with suppress(TelegramBadRequest):
        order_full_text = OrderMsgBuilderFactory.get_builder(
            order=order, items=order.items_details
        ).build_full_message()
        await callback_query.message.edit_text(
            order_full_text,
            reply_markup=make_user_order_inline_kb(
                order_id=order.id, status=order.status
            ),
        )
