from apscheduler.schedulers.asyncio import AsyncIOScheduler

from db_handler.db_class import db_handler


def scheduler_setup():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(db_handler.update_items_table, "interval", minutes=1)
    scheduler.start()
