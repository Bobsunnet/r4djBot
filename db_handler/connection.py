import sqlite3
from logging import getLogger

logger = getLogger(__name__)


class SqliteConnection:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.connection = sqlite3.connect(self.db_name)
        self.connection.row_factory = sqlite3.Row  # Enable row access by name
        self.connection.execute("PRAGMA foreign_keys = ON;")
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.connection.commit()
        else:
            self.connection.rollback()
            logger.error(f"Database error: {exc_value}")

        self.connection.close()
