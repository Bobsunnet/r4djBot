from logging import getLogger
from typing import List

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from db_handler.models import Item, Order, User
from db_handler.schemas.order import OrderCreate
from db_handler.schemas.user import UserCreate

logger = getLogger(__name__)


async def get_items(session: AsyncSession) -> List[Item]:
    stmt = select(Item).order_by(Item.row_order)
    result: Result = await session.execute(stmt)
    items = result.scalars().all()
    return list(items)


async def get_user_by_tg_id(session: AsyncSession, user_id: int) -> User:
    stmt = select(User).where(User.user_id == user_id)
    result: Result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(session: AsyncSession, user: UserCreate) -> User:
    user = User(**user.model_dump())
    session.add(user)
    await session.commit()
    return user


async def create_order(session: AsyncSession, order: OrderCreate) -> Order:
    order = Order(**order.model_dump())
    session.add(order)
    await session.commit()
    return order
