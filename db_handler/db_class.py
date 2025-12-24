import logging
import sqlite3
import requests

URL_SHEET = "https://script.google.com/macros/s/AKfycbyIqo_k_VKMYcqZSiVhiQvsbYlwE0G6OjbvBDeYWZ7Fk09J4lMRXKy1bwK8gRA2Y6SkgA/exec"
logger = logging.getLogger(__name__)

def download_sheets_data(url: str)->list:
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            logging.error(f"Failed to download data, status code: {response.status_code}")
            return []
        
    except requests.RequestException as e:
        logging.error(f"Error downloading data: {e}")
        return []
    

def get_prices_data()->list:
    return filter(lambda row: row[3] or row[4], 
                  download_sheets_data(URL_SHEET)[1:])
  

class SqliteConnection:
    def __init__(self, db_name:str):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.connection = sqlite3.connect(self.db_name)
        self.connection.execute("PRAGMA foreign_keys = ON;")
        self.cursor = self.connection.cursor()
        return self.cursor
    
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.connection.commit()
        else:
            self.connection.rollback()
            logging.error(f"Database error: {exc_value}")
        
        self.connection.close()


class DBHandler:
    sync_on = False

    def __init__(self, db_name:str):
        self.db_name = db_name
        self.update_table()

    def _get_cursor(self):
        return SqliteConnection(self.db_name)

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

    def update_table(self):
        if not self.sync_on:
            logger.warning("Sync is turned off. Skipping database update.")
            return
        
        data = get_prices_data()
        if data:
            with self._get_cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS items (
	                "id"	INTEGER NOT NULL,
	                "hash_code"	VARCHAR(10),
	                "name"	VARCHAR(300) NOT NULL,
	                "desc"	VARCHAR(512),
	                "amount"	INTEGER NOT NULL,
	                "price"	INTEGER NOT NULL,
	                PRIMARY KEY("id"),
                    UNIQUE("hash_code")
                    );
                """)
                cursor.execute("DELETE FROM items")
                for item in data:
                    cursor.execute("""
                        INSERT INTO items (hash_code, name, desc, amount, price)
                        VALUES (?, ?, ?, ?, ?)
                    """, (item[0], item[1], item[2], int(item[3]), int(item[4])))
                logger.info("Database updated successfully.")


db_handler = DBHandler("r4DB.db")