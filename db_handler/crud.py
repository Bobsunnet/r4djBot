from logging import getLogger
from typing import List

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from db_handler.models import Item, Order, OrderItemAssociation, OrderStatus, User
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


async def create_order_with_items(
    session: AsyncSession, order: OrderCreate, items: List[dict]
) -> Order:
    order_db = Order(**order.model_dump())
    session.add(order_db)
    await session.flush()  # to get order.id

    for item in items:
        session.add(
            OrderItemAssociation(
                order_id=order_db.id,
                item_hash_code=item.get("hash_code"),
                quantity=item.get("quantity"),
                unit_price=item.get("price"),
            )
        )

    await session.commit()
    return order_db


async def get_orders_with_status(
    session: AsyncSession, status: OrderStatus
) -> List[Order]:
    """
    Get all orders with a specific status. With user loaded

    Args:
        session: AsyncSession
        status: OrderStatus enum value

    Returns:
        List[Order]
    """
    stmt = select(Order).options(joinedload(Order.user)).where(Order.status == status)
    result: Result = await session.execute(stmt)
    orders = result.scalars().all()
    return list(orders)


async def get_order_by_id(session: AsyncSession, order_id: int) -> Order | None:
    stmt = select(Order).where(Order.id == order_id)
    result: Result = await session.execute(stmt)
    return result.scalar_one_or_none()


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
        select(Order)
        .options(
            selectinload(Order.items_details).joinedload(OrderItemAssociation.item)
        )
        .where(Order.user_id == user_id)
    )
    result: Result = await session.execute(stmt)
    orders = result.scalars().all()
    return list(orders)
