import logging

from .api_calls import get_prices_data
from .connection import SqliteConnection

logger = logging.getLogger(__name__)


class DBHandler:
    sync_on = False

    def __init__(self, db_name: str):
        self.db_name = db_name
        self.create_db()
        self.update_items_table()

    def _get_cursor(self):
        return SqliteConnection(self.db_name)

    def read_all(self, table_name: str = "items") -> list:
        """Read all rows from the specified table."""
        with self._get_cursor() as cursor:
            query = f"SELECT * FROM {table_name}"
            cursor.execute(query)
            return cursor.fetchall()

    def read_item_by_id(self, item_id: int) -> dict:
        with self._get_cursor() as cursor:
            cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
            return cursor.fetchone()

    def create_user(
        self, user_id: int, first_name: str, last_name: str, phone_number: str
    ) -> None:
        with self._get_cursor() as cursor:
            query = "INSERT INTO users (user_id, first_name, last_name, phone_number) VALUES (?, ?, ?, ?)"
            cursor.execute(query, (user_id, first_name, last_name, phone_number))

    def read_user_by_user_id(self, user_id: int) -> dict:
        with self._get_cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            return cursor.fetchone()

    def update_items_table(self):
        if not self.sync_on:
            logger.warning("SYNC IS OFF. Skipping database update.")
            return

        data = get_prices_data()
        if data:
            with self._get_cursor() as cursor:
                cursor.execute("DELETE FROM items")
                for item in data:
                    cursor.execute(
                        """
                        INSERT INTO items (hash_code, name, desc, amount, price)
                        VALUES (?, ?, ?, ?, ?)
                    """,
                        (item[0], item[1], item[2], int(item[3]), int(item[4])),
                    )
                logger.info("Database updated successfully.")

    def create_db(self):
        with self._get_cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS items (
                "id" INTEGER NOT NULL,
                "hash_code" VARCHAR(10),
                "name" VARCHAR(300) NOT NULL,
                "desc" VARCHAR(512),
                "amount" INTEGER NOT NULL,
                "price" INTEGER NOT NULL,
                PRIMARY KEY("id"),
                UNIQUE("hash_code")
                );
            """)
            logger.info("Items table exists or created successfully.")

        with self._get_cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                "id" INTEGER NOT NULL,
                "user_id" INTEGER NOT NULL,
                "first_name" VARCHAR(128),
                "last_name" VARCHAR(128),
                "phone_number" VARCHAR(128),
                PRIMARY KEY("id")
                );
            """)
            logger.info("Users table exists or created successfully.")


db_handler = DBHandler("r4DB.db")
