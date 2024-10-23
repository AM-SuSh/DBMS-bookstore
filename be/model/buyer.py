import time
import uuid
import json
import logging
from be.model import db_conn
from be.model import error
from pymongo import errors

class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(
        self, user_id: str, store_id: str, id_and_count: [(str, int)]
    ) -> (int, str, str):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            for book_id, count in id_and_count:
                book = self.conn.store.find_one({"store_id": store_id, "book_id": book_id})
                if book is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = book.get("stock_level")

                price_info = book.get("book_info")
                price = json.loads(price_info).get("price") #if price_info else None

                if stock_level is None or stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                result = self.conn.store.update_one(
                    {"store_id": store_id, "book_id": book_id, "stock_level": {"$gte": count}},
                    {"$inc": {"stock_level": -count}}
                )

                if result.modified_count == 0:
                    return error.error_stock_level_low(book_id) + (order_id,)

                self.conn.new_order_detail.insert_one({
                    "order_id": uid,
                    "book_id": book_id,
                    "count": count,
                    "price": price
                })

            self.conn.new_order.insert_one({
                "order_id": uid,
                "store_id": store_id,
                "user_id": user_id,
                "condition": 0,
                "time": time.time()
            })

            order_id = uid

        except errors.PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""

        return 200, order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            order = self.conn.new_order.find_one({"order_id": order_id})
            if order is None:
                return error.error_invalid_order_id(order_id)

            order_id = order["order_id"]
            buyer_id = order["user_id"]
            store_id = order["store_id"]

            if buyer_id != user_id:
                return error.error_authorization_fail()

            user = self.conn.user.find_one({"user_id": buyer_id})
            if user is None:
                return error.error_non_exist_user_id(buyer_id)

            if password != user["password"]:
                return error.error_authorization_fail()

            balance = user["balance"]
            store = self.conn.user_store.find_one({"store_id": store_id})
            if store is None:
                return error.error_non_exist_store_id(store_id)

            seller_id = store["user_id"]

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            order_details = list(self.conn.new_order_detail.find({"order_id": order_id}))
            total_price = sum(detail["price"] * detail["count"] for detail in order_details)

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            result = self.conn.user.update_one(
                {"user_id": buyer_id, "balance": {"$gte": total_price}},
                {"$inc": {"balance": -total_price}}
            )
            if result.modified_count == 0:
                return error.error_not_sufficient_funds(order_id)

            result = self.conn.user.update_one(
                {"user_id": seller_id},
                {"$inc": {"balance": total_price}}
            )
            if result.modified_count == 0:
                return error.error_non_exist_user_id(seller_id)

            self.conn.new_order.delete_one({"order_id": order_id})
            self.conn.new_order_detail.delete_many({"order_id": order_id})

        except errors.PyMongoError as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            user = self.conn.user.find_one({"user_id": user_id})
            if user is None:
                return error.error_authorization_fail()

            if user["password"] != password:
                return error.error_authorization_fail()

            result = self.conn.user.update_one(
                {"user_id": user_id},
                {"$inc": {"balance": add_value}}
            )
            if result.modified_count == 0:
                return error.error_non_exist_user_id(user_id)

        except errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"
