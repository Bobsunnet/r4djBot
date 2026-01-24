from logging import getLogger
from typing import List

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from db_handler.models import Item, Order, OrderStatus, User
from db_handler.schemas.order import OrderCreate
from db_handler.schemas.user import UserCreate

logger = getLogger(__name__)


async def get_items(session: AsyncSession) -> List[Item]:
    stmt = select(Item).order_by(Item.row_order)
    result: Result = await session.execute(stmt)
    items = result.scalars().all()
    return list(items)


async def get_user_by_tg_id(session: AsyncSession, user_id: int) -> User | None:
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


async def get_pending_orders(session: AsyncSession) -> List[Order]:
    """
    Get all pending orders. With user loaded

    Args:
        session: AsyncSession

    Returns:
        List[Order]
    """
    stmt = (
        select(Order)
        .options(joinedload(Order.user))
        .where(Order.status == OrderStatus.PENDING)
    )
    result: Result = await session.execute(stmt)
    orders = result.scalars().all()
    return list(orders)


async def get_orders_by_userid(
    session: AsyncSession, user_id: int
) -> List[Order] | None:
    """
    Get all orders for a specific user by user telegram ID.

    Args:
        session: AsyncSession
        user_id: User TELEGRAM ID !!!

    Returns:
        List[Order]
    """
    stmt = (
        select(User).options(selectinload(User.orders)).where(User.user_id == user_id)
    )
    result: Result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        return

    return user.orders
