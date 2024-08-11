import os
import sqlite3

from dotenv import load_dotenv

from location_util import Location
from tgtg_client import Store, Interval, Item


class TGTG_DB:
    def __init__(self):
        load_dotenv()
        self.db_name = f"{os.getenv('DB_NAME')}.db"
        self.create_db()

    def create_db(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                        CREATE TABLE IF NOT EXISTS stores (
                            id VARCHAR PRIMARY KEY,
                            name VARCHAR,
                            address VARCHAR
                        )
                        """)
            cursor.execute("""
                        CREATE TABLE IF NOT EXISTS locations (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            latitude FLOAT,
                            longitude FLOAT,
                            full_address VARCHAR
                        )
                        """)
            cursor.execute("""
                        CREATE TABLE IF NOT EXISTS items (
                            id VARCHAR PRIMARY KEY,
                            name VARCHAR,
                            display_name VARCHAR,
                            description VARCHAR,
                            collection_info VARCHAR,
                            amount INTEGER,
                            price FLOAT,
                            currency VARCHAR,
                            pickup_start VARCHAR,
                            pickup_end VARCHAR,
                            store_id VARCHAR,
                            FOREIGN KEY (store_id) REFERENCES stores(id)
                        )
                        """)
            conn.commit()

    def add_store(self, store: Store):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO stores (id, name, address) VALUES (?, ?, ?)",
                           (store.id, store.name, store.address))
            conn.commit()

    def list_stores(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, address FROM stores")
            stores = cursor.fetchall()
        return [Store({'store_id': id, 'store_name': name, 'store_location': {'address': {'address_line': address}}})
                for id, name, address in stores]

    def get_store_by_id(self, store_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, address FROM stores WHERE id = ?", (store_id,))
            store = cursor.fetchone()
        if store:
            return Store({'store_id': store[0], 'store_name': store[1],
                          'store_location': {'address': {'address_line': store[2]}}})
        return None

    def remove_store(self, store_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM stores WHERE id = ?", (store_id,))
            conn.commit()

    def add_location(self, location: Location):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO locations (latitude, longitude, full_address) VALUES (?, ?, ?)",
                           (location.latitude, location.longitude, location.full_address))
            conn.commit()

    def list_locations(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, latitude, longitude, full_address FROM locations")
            locations = cursor.fetchall()
        return [Location(latitude, longitude, full_address) for _, latitude, longitude, full_address in locations]

    def get_location_by_id(self, location_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, latitude, longitude, full_address FROM locations WHERE id = ?", (location_id,))
            location = cursor.fetchone()
        if location:
            return Location(location[1], location[2], location[3])
        return None

    def remove_location(self, location_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM locations WHERE id = ?", (location_id,))
            conn.commit()

    def add_item(self, item: Item):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO items (id, 
            name, 
            display_name, 
            description, 
            collection_info, 
            amount, 
            price, 
            currency, 
            pickup_start, 
            pickup_end, 
            store_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                           (item.id, item.name, item.display_name, item.description, item.collection_info, item.amount,
                            item.price, item.currency,
                            item.pickup_interval.start.isoformat() if item.pickup_interval else None,
                            item.pickup_interval.end.isoformat() if item.pickup_interval else None,
                            item.store.id))
            conn.commit()

    def list_items(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM items")
            items = cursor.fetchall()
        return [self._create_item_from_row(row) for row in items]

    def get_item_by_id(self, item_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
            item = cursor.fetchone()
        if item:
            return self._create_item_from_row(item)
        return None

    def remove_item(self, item_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
            conn.commit()

    def _create_item_from_row(self, row):
        item_id, name, display_name, description, collection_info, amount, price, currency, pickup_start, pickup_end, store_id = row
        store = self.get_store_by_id(store_id)
        pickup_interval = Interval.from_iso_strings(pickup_start, pickup_end) if pickup_start and pickup_end else None
        return Item({
            'item': {
                'item_id': item_id,
                'name': name,
                'description': description,
                'collection_info': collection_info,
                'items_available': amount,
                'item_price': {
                    'minor_units': int(price * (10 ** 2)),
                    'decimals': 2,
                    'code': currency
                }
            },
            'display_name': display_name,
            'pickup_interval': {
                'start': pickup_start,
                'end': pickup_end
            },
            'store': {
                'store_id': store.id,
                'store_name': store.name,
                'store_location': {
                    'address': {
                        'address_line': store.address
                    }
                }
            }
        })


if __name__ == "__main__":
    db = TGTG_DB()

