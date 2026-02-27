from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import settings
from db_handler.bulk_operations import (
    bulk_insert_items,
    change_active_order_to_completed,
)


def setup_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        bulk_insert_items, "interval", minutes=settings.db.sync_db_interval
    )
    scheduler.add_job(
        change_active_order_to_completed,
        "cron",
        hour=2,
        minute=0,
    )
    scheduler.start()

