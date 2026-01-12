from typing import List

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from db_handler.models import Item, User


async def get_items(session: AsyncSession) -> List[Item]:
    stmt = select(Item).order_by(Item.id)
    result: Result = await session.execute(stmt)
    items = result.scalars().all()
    return list(items)


async def get_user_by_tg_id(session: AsyncSession, user_id: int) -> User:
    stmt = select(User).where(User.user_id == user_id)
    result: Result = await session.execute(stmt)
    return result.scalar_one_or_none()
