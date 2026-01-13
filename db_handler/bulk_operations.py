from logging import getLogger

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
    column_names = ["hash_code", "name", "desc", "amount", "price"]

    if data:
        data_dict = [dict(zip(column_names, row)) for row in data]
        async with db_helper.engine.connect() as conn:
            table_object = Item.__table__
            await conn.execute(table_object.delete())
            await conn.execute(table_object.insert(), data_dict)
            await conn.commit()

        logger.info("SYNC IS ON. Database SYNCED successfully.")
