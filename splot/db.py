import os
from pprint import pprint

from pymongo import MongoClient


class SplotDb:
    def __init__(self, db):
        self.db = db

    def create_indexes(self):
        self.db.playlists.create_index("id", unique=True)

    def upsert_playlist(self, playlist):
        print(f"Upserting playlist {playlist['name']}")
        f = {"id": playlist["id"]}
        result = self.db.playlists.replace_one(f, playlist, upsert=True)
        pprint(result.raw_result)


def splot_db():
    uri = os.environ["SPLOT_MONGODB_URI"]
    dbname = os.environ["SPLOT_MONGODB_DB"]
    client = MongoClient(uri)
    return SplotDb(client[dbname])
