import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from db_handler import crud
from db_handler.models import Order, User
from db_handler.schemas.order import OrderCreate, OrderUpdate

logger = logging.getLogger(__name__)

async def process_order_submission(
    user: User,
    state_data: dict,
    items: List[dict],
    order_for_edit: Order | None,
    session: AsyncSession,
):

    if not order_for_edit:
        order_dto = OrderCreate(
            user_id=user.user_id,
            date_start=state_data["date_start"],
            date_end=state_data["date_end"],
            work_days=state_data["work_days"],
            address=state_data["address"],
            description=state_data["comment"],
        )
        order = await crud.create_order_with_items(session=session, order=order_dto, items=items)
        logger.info(f"[ORDER] ORDER FROM {user.name} {user.surname} ({user.user_id}) created: {order_dto}")

    else:
        order_dto = OrderUpdate(
            id = order_for_edit.id,
            user_id=user.user_id,
            date_start=state_data["date_start"],
            date_end=state_data["date_end"],
            work_days=state_data["work_days"],
            address=state_data["address"],
            description=state_data["comment"],
        )

        order = await crud.update_order_with_items(order_update=order_dto, items=items, session=session)
        logger.info(f"[ORDER] ORDER FROM {user.name} {user.surname} ({user.user_id}) updated: {order_dto}")

    return await crud.get_order_with_items(session=session, order_id=order.id)


