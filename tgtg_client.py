import os

from tgtg import TgtgClient

from dotenv import load_dotenv


class TGTG:
    def __init__(self):
        load_dotenv()
        self.client = TgtgClient(email=os.getenv("TGTG_EMAIL"))
        self.credentials = self.client.get_credentials()

    def test(self):
        self.client.get_items()


if __name__ == "__main__":
    client = TGTG()
