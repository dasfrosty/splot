from pymongo import MongoClient
import os


class SplotDb:
    def __init__(self, db):
        self.db = db

    def create_indexes(self):
        self.db.playlists.create_index("id", unique=True)

    def upsert_playlist(self, playlist):
        q = {"id": playlist["id"]}
        self.db.playlists.update_one(q, {"$set": playlist}, upsert=True)


def splot_db():
    uri = os.environ["SPLOT_MONGODB_URI"]
    dbname = os.environ["SPLOT_MONGODB_DB"]
    client = MongoClient(uri)
    return SplotDb(client[dbname])
