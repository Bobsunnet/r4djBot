import logging
import sqlite3
from contextlib import contextmanager


class DBHandler:
    def __init__(self, db_name:str):
        self.db_name = db_name

    @contextmanager
    def _get_cursor(self):
        conn = sqlite3.connect(self.db_name)
        try:
            cursor = conn.cursor()
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            logging.error(f"Database error: {e}")
            raise e
        finally:
            conn.close()


    def read_all(self, table_name:str = "items"):
        with self._get_cursor() as cursor:
            query = f"SELECT * FROM {table_name}"
            cursor.execute(query)
            return cursor.fetchall()
    
    def read_by_id(self, item_id:int, table_name:str = "items"):
        with self._get_cursor() as cursor:
            query = f"SELECT * FROM {table_name} WHERE id = ?"
            cursor.execute(query, (item_id,))
            return cursor.fetchone()


db_handler = DBHandler("r4DB.db")