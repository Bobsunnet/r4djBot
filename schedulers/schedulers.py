from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import SYNC_DB_INTERVAL
from db_handler.db_class import db_handler


def scheduler_setup():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        db_handler.update_items_table, "interval", minutes=SYNC_DB_INTERVAL
    )
    scheduler.start()
