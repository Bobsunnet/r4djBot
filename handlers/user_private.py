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

# from keyboards.inline import make_user_order_inline_kb
# from utils.order_msg_builder import OrderMsgBuilderFactory

user_private_router = Router()


# @user_private_router.message(Command("orders"))
# async def orders_list(message: Message, session: AsyncSession):
#     orders = await crud.get_orders_by_userid(
#         session=session, user_id=message.from_user.id
#     )

#     if not orders:
#         await message.answer("У вас немає активних замовлень")
#         return

#     for order in orders:
#         await message.answer(
#             OrderMsgBuilderFactory.get_builder(
#                 order, order.items_details
#             ).build_preview_message(),
#             reply_markup=make_user_order_inline_kb(
#                 order_id=order.id, status=order.status.value
#             ),
#         )


@user_private_router.message(Command("orders"))
async def orders_list(message: Message, session: AsyncSession):
    orders = await crud.get_orders_by_userid(
        session=session, user_id=message.from_user.id
    )

    if not orders:
        await message.answer("У вас ще немає замовлень")
        return

    await message.answer(
        "Please select a date: ",
        reply_markup=await DialogCalendar(
            locale=await get_user_locale(message.from_user)
        ).start_calendar(),
    )


# dialog calendar usage
@user_private_router.callback_query(DialogCalendarCallback.filter())
async def process_dialog_calendar(
    callback_query: CallbackQuery, callback_data: CallbackData
):
    selected, date = await DialogCalendar(
        locale=await get_user_locale(callback_query.from_user)
    ).process_selection(callback_query, callback_data)
    if selected:
        print("Selected", date.month)
        await callback_query.message.answer(f"You selected {date.strftime('%m/%Y')}")
