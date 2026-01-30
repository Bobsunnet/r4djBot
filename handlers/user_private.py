from aiogram import Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from aiogram_calendar import (
    DialogCalendar,
    DialogCalendarCallback,
    get_user_locale,
)
from db_handler import crud
from keyboards.inline import make_user_order_inline_kb
from utils.order_msg_builder import OrderUserMsgBuilder
from utils.utils import create_orders_count_dict

user_private_router = Router()


@user_private_router.message(Command("orders"))
async def orders_list(message: Message, session: AsyncSession):
    if not await crud.get_orders_by_userid(
        session=session, user_id=message.from_user.id
    ):
        await message.answer("У вас ще немає замовлень")
        return

    await message.answer(
        "Оберіть місяць: ",
        reply_markup=await DialogCalendar(locale=await get_user_locale(message.from_user)).start_calendar(),
    )


@user_private_router.callback_query(DialogCalendarCallback.filter())
async def process_order_calendar_user(
    callback_query: CallbackQuery,
    callback_data: CallbackData,
    session: AsyncSession,
):
    orders = await crud.get_orders_by_userid(
        session=session, user_id=callback_query.from_user.id
    )

    selected, date = await DialogCalendar(
        locale=await get_user_locale(callback_query.from_user),
        orders_count_dict=create_orders_count_dict(orders)
    ).process_selection(callback_query, callback_data)
    if not selected:
        return

    orders_for_month = await crud.get_orders_by_userid_and_date_start(
        session=session,
        user_id=callback_query.from_user.id,
        date=date,
    )
    if not orders_for_month:
        await callback_query.message.answer(f"Замовлень за {date.strftime('%m/%Y')} не знайдено.")
        await callback_query.message.delete()
        return

    for order in orders_for_month:
        await callback_query.message.answer(
            OrderUserMsgBuilder(order, order.items_details).build_preview_message(),
            reply_markup=make_user_order_inline_kb(
                order_id=order.id,
                status=order.status,
            ),
        )
    await callback_query.message.delete()
