from logging import getLogger

from sqlalchemy import delete, func
from sqlalchemy.dialects.postgresql import insert

from config import settings
from db_handler.api_calls import get_prices_data
from db_handler.db_helper import db_helper
from db_handler.models import Base, Item

logger = getLogger(__name__)


async def create_db():
    """Create database."""
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def bulk_insert_items():
    """Bulk insert items into the database. Delete all existing items first."""
    if not settings.db.sync_db:
        logger.warning("SYNC IS OFF. Skipping database update.")
        return

    data = get_prices_data()
    column_names = ["hash_code", "name", "description", "amount", "price"]

    if not data:
        return

    sync_time = func.now()

    data_dict = [
        {"row_order": i, "last_seen_at": sync_time, **dict(zip(column_names, row))}
        for i, row in enumerate(data, start=1)
    ]

    table = Item.__table__
    stmt = insert(table).values(data_dict)
    stmt = stmt.on_conflict_do_update(
        index_elements=[table.c.hash_code],
        set_={
            "row_order": stmt.excluded.row_order,
            "name": stmt.excluded.name,
            "description": stmt.excluded.description,
            "amount": stmt.excluded.amount,
            "price": stmt.excluded.price,
            "last_seen_at": sync_time,
        },
    )
    async with db_helper.engine.begin() as conn:
        await conn.execute(stmt)
        await conn.execute(delete(table).where(table.c.last_seen_at < sync_time))
        logger.info("SYNC IS ON. Database SYNCED successfully.")
