from be.model import store
from pymongo import MongoClient

class DBConn:
    def __init__(self):
        self.conn = store.get_db_conn()
    def user_id_exist(self, user_id):
        user = self.conn.user.find_one({"user_id": user_id})
        return user is not None

    def book_id_exist(self, store_id, book_id):
        result = self.conn.store.find_one({"store_id": store_id, "book_id": book_id})
        return result is not None

    def store_id_exist(self, store_id):
        store = self.conn.user_store.find_one({"store_id": store_id})
        return store is not None
