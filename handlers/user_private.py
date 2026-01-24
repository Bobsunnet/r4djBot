from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from db_handler import crud
from keyboards.keyboard import make_wo_auth_kb
from utils import messages as ms
from utils import utils

user_private_router = Router()


@user_private_router.message(Command("orders"))
async def orders_list(message: Message, session: AsyncSession):
    user = await crud.get_user_by_tg_id(session=session, user_id=message.from_user.id)
    if not user:
        await message.answer(
            ms.not_authorized_message,
            reply_markup=make_wo_auth_kb(),
        )
        return

    orders = await crud.get_orders_by_userid(session=session, user=user)

    if not orders:
        await message.answer("У вас немає активних замовлень")
        return

    for order in orders:
        # await message.answer(utils.create_order_message(order))
        await message.answer(str(order))
