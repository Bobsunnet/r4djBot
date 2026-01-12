from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import settings
from db_handler.db_class import db_handler


def scheduler_setup():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        db_handler.update_items_table, "interval", minutes=settings.db.sync_db_interval
    )
    scheduler.start()
