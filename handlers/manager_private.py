from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from db_handler import crud
from utils import utils

manager_router = Router()


@manager_router.message(Command("pending_orders"))
async def pending_orders_list(message: Message, session: AsyncSession):
    if message.from_user.id != settings.telegram.manager_id:
        await message.answer("Ви не маєте доступу до цієї команди")
        return

    orders = await crud.get_pending_orders(session=session)

    if not orders:
        await message.answer("У вас немає нових замовлень")
        return

    for order in orders:
        await message.answer(
            utils.format_order_message_for_admin(user=order.user, order=order, items=[])
        )
