from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from db_handler import crud
from utils import utils

user_private_router = Router()


@user_private_router.message(Command("orders"))
async def orders_list(message: Message, session: AsyncSession):
    orders = await crud.get_orders_by_userid(
        session=session, user_id=message.from_user.id
    )

    if not orders:
        await message.answer("У вас немає активних замовлень")
        return

    for order in orders:
        await message.answer(utils.build_order_message_body(order, []))
