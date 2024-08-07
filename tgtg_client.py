import os
import sys

import location_util
from datetime import datetime, timezone
from dateutil import parser

from tgtg import TgtgClient

from dotenv import load_dotenv


class TGTG:
    def __init__(self):
        load_dotenv()
        self.client = TgtgClient(email=os.getenv("TGTG_EMAIL"))
        self.credentials = self.client.get_credentials()

    def get_items(self, loc: location_util.Location, radius=10):
        res = []
        page = 1
        page_size = 400

        while len(res) == (page - 1) * page_size:
            res += self.client.get_items(
                latitude=loc.latitude,
                longitude=loc.longitude,
                radius=radius,
                favorites_only=False,
                page_size=page_size,
                page=page
            )
            page += 1

        return res


class Item:
    def __init__(self, tgtgItem):
        iteminfo = tgtgItem.get('item', {})
        self.id: str = iteminfo.get('item_id')
        self.name: str = iteminfo.get('name')
        self.display_name: str = tgtgItem.get('display_name')
        self.description: str = iteminfo.get('description')
        self.collection_info: str = iteminfo.get('collection_info')
        self.amount: int = tgtgItem.get('items_available')

        priceinfo = iteminfo.get('item_price', {})
        self.price: float = float(priceinfo.get('minor_units', 0)) / (10 ** int(priceinfo.get('decimals', 0)))
        self.currency: str = priceinfo.get('code')

        pickup_interval_info = tgtgItem.get('pickup_interval', {})
        start = pickup_interval_info.get('start')
        end = pickup_interval_info.get('end')
        self.pickup_interval = Interval.from_iso_strings(start, end) if start and end else None

        store_info = tgtgItem.get('store', {})
        self.store = Store(store_info)

    def has_expired(self) -> bool:
        if self.pickup_interval is None:
            return False
        return self.pickup_interval.is_after()

    def __str__(self):
        return f"""store: {self.store}
        name: {self.name}
        price: {self.price} {self.currency}
        amount left: {self.amount}
        description: {self.description}
        collection: {self.collection_info}
        pickup interval: {self.pickup_interval}
        address: {self.store.address}
        """


class Store:
    def __init__(self, storeinfo):
        self.id: str = storeinfo.get('store_id')
        self.name: str = f"{storeinfo.get('branch', '')} {storeinfo.get('store_name', '')}"
        address_info = storeinfo.get('store_location', {}).get('address', {})
        self.address: str = address_info.get('address_line')

    def __str__(self):
        return self.name


class Interval:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    @classmethod
    def from_iso_strings(cls, start_str, end_str):
        start = parser.isoparse(start_str)
        end = parser.isoparse(end_str)
        return cls(start, end)

    def is_before(self, comparison_time=datetime.now(timezone.utc)):
        return comparison_time < self.start

    def is_during(self, comparison_time=datetime.now(timezone.utc)) -> bool:
        return self.start <= comparison_time <= self.end

    def is_after(self, comparison_time=datetime.now(timezone.utc)) -> bool:
        return comparison_time > self.end

    def __str__(self):
        if sys.platform.startswith('win'):
            start_str = self.start.strftime('%b %d, %#H:%M')
            end_str = self.end.strftime('%#H:%M')
        else:
            start_str = self.start.strftime('%b %d, %-H:%M')
            end_str = self.end.strftime('%-H:%M')

        if self.start.date() == self.end.date():
            return f"{start_str}-{end_str}"
        else:
            if sys.platform.startswith('win'):
                start_date_str = self.start.strftime('%b %d, %#H:%M')
                end_date_str = self.end.strftime('%b %d, %#H:%M')
            else:
                start_date_str = self.start.strftime('%b %d, %-H:%M')
                end_date_str = self.end.strftime('%b %d, %-H:%M')

            return f"{start_date_str} - {end_date_str}"


if __name__ == "__main__":
    client = TGTG()

    while True:
        location = location_util.get_location_from_string(input("enter location: "))
        get_items = client.get_items(location)
        items: [Item] = map(lambda x: Item(x), get_items)

        for i in items:
            if i.pickup_interval is not None:
                print(f"{i.pickup_interval}: {i.has_expired()}")

