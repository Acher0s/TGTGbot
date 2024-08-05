import os
import location_util

from tgtg import TgtgClient

from dotenv import load_dotenv


class TGTG:
    def __init__(self):
        load_dotenv()
        self.client = TgtgClient(email=os.getenv("TGTG_EMAIL"))
        self.credentials = self.client.get_credentials()

    def get_items(self, loc: location_util.Location, radius=10):
        return self.client.get_items(
            latitude=loc.latitude,
            longitude=loc.longitude,
            radius=radius,
            favorites_only=False,
            page_size=400,
        )


if __name__ == "__main__":
    client = TGTG()

    while True:
        i = 0

        location = location_util.get_location_from_string(input("enter location: "))
        items = client.get_items(location)
        file = open(f"./items/items{i}.json", "a", encoding="utf-8")
        file.write(str(items))
        file.close()
        i += 1
