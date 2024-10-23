import logging
import os
import sqlite3 as sqlite
import threading
from pymongo import MongoClient
from pymongo import errors


class Store:

    def __init__(self, db_uri: str, db_name: str):
        self.client = MongoClient(db_uri)
        self.database = self.client[db_name]
        self.init_tables()
    def init_tables(self):
        try:
            user = self.database.get_collection("user")
            store = self.database.get_collection("store")
            user_store = self.database.get_collection("user_store")
            new_order = self.database.get_collection("new_order")
            new_order_detail = self.database.get_collection("new_order_detail")
        except ConnectionError as e:
            logging.error("Could not connect to MongoDB: %s", e)
    def get_db_conn(self):
        return self.database



database_instance: Store = None
# global variable for database sync
init_completed_event = threading.Event()


def init_database(db_uri, db_name):
    global database_instance
    database_instance = Store(db_uri, db_name)


def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()


if __name__ == "__main__":
    init_database('mongodb://localhost:27017/', 'bookstore')
    print("connect done")

