from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import settings
from db_handler.bulk_operations import bulk_insert_items


def scheduler_setup():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        bulk_insert_items, "interval", minutes=settings.db.sync_db_interval
    )
    scheduler.start()
