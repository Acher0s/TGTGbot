import os
import sqlite3

from dotenv import load_dotenv


class TGTG_DB:
    def __init__(self):
        load_dotenv()
        self.db_name = f"{os.getenv("DB_NAME")}.db"
        self.create_db()

    def create_db(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS channels (
                id VARCHAR,
                name VARCHAR NOT NULL,
                PRIMARY KEY (id)
            )
            """)
            conn.commit()

    def add_channel(self, channel_id, channel_name):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO channels (id, name) VALUES (?, ?)", (channel_id, channel_name))
                conn.commit()
            except sqlite3.IntegrityError:
                print("Channel already exists")

    def remove_channel(self, channel_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM channels WHERE id = ?", (channel_id,))
            conn.commit()

    def list_channels(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM channels")
            channels = cursor.fetchall()
        return channels


if __name__ == "__main__":
    db = TGTG_DB()

    db.add_channel("1", "Channel One")
    db.add_channel("2", "Channel Two")

    print("Channels:", db.list_channels())

    db.remove_channel("1")

    print("Channels after removal:", db.list_channels())
