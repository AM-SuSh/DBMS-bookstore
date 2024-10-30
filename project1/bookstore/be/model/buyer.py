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
        book_id_list = []
        total_price = 0
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
                price = json.loads(price_info).get("price")
                book_id_list.append(book_id)
                total_price += price * count

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
            })

            self.conn.order.insert_one({
                    "order_id": uid,
                    "user_id": user_id,
                    "store_id": store_id,
                    "book_id_list": book_id_list,
                    "total_price": total_price,
                    "condition": "new order",
                    "time": time.time()
                })

            order_id = uid

        except errors.PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            order = self.conn.new_order.find_one({"order_id": order_id})
            if order is None:
                return error.error_invalid_order_id(order_id)

            order_id = order["order_id"]
            buyer_id = order["user_id"]
            store_id = order["store_id"]

            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            user = self.conn.user.find_one({"user_id": buyer_id})
            if password != user["password"]:
                return error.error_authorization_fail()

            balance = user["balance"]
            store = self.conn.user_store.find_one({"store_id": store_id})
            seller_id = store["user_id"]

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
            #logging.info(f"Payment processed successfully for order_id: {order_id}")

        except errors.PyMongoError as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            user = self.conn.user.find_one({"user_id": user_id})
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

    def order_confirm(self, order_id, now_time, will):
        try:
            order = self.conn.order.find_one({"order_id": order_id})
            if order is None:
                return error.error_invalid_order_id(order_id)

            order_time = order["time"]

            if now_time > order_time + 900:
                self.conn.order.update_one(
                    {"order_id": order_id},
                    {"$set": {"condition": "overtime-close"}}
                )
                book_id_list = order["book_id_list"]
                store_id = order["store_id"]
                for i in book_id_list:
                    count = self.conn.new_order_detail.find_one({"order_id": order_id,"book_id": i}).get("count")
                    self.conn.store.update_one(
                        {"store_id": store_id, "book_id": i, "stock_level": {"$gte": count}},
                        {"$inc": {"stock_level": + count}}
                    )

            else:
                if will == "confirm":
                    self.conn.order.update_one(
                        {"order_id": order_id},
                        {"$set": {"condition": will}}
                    )
                elif will == "cancel":
                    self.conn.order.update_one(
                        {"order_id": order_id},
                        {"$set": {"condition": will}}
                    )
                    book_id_list = order["book_id_list"]
                    store_id = order["store_id"]
                    for i in book_id_list:
                        count = self.conn.new_order_detail.find_one({"order_id": order_id, "book_id": i}).get("count")
                        self.conn.store.update_one(
                            {"store_id": store_id, "book_id": i, "stock_level": {"$gte": count}},
                            {"$inc": {"stock_level": + count}}
                        )
                else:
                    return error.error_invalid_input(will)
        except errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def payment_buyer(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            order = self.conn.order.find_one({"order_id": order_id})
            if order is None:
                return error.error_invalid_order_id(order_id)

            order_id = order["order_id"]
            buyer_id = order["user_id"]

            if buyer_id != user_id:
                return error.error_authorization_fail()
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            user = self.conn.user.find_one({"user_id": buyer_id})
            if password != user["password"]:
                return error.error_authorization_fail()

            total_price = order["total_price"]
            condition = order["condition"]

            if condition == "confirm":
                balance = user["balance"]
                if balance < total_price:
                    return error.error_not_sufficient_funds(order_id)
                result = self.conn.user.update_one(
                    {"user_id": buyer_id, "balance": {"$gte": total_price}},
                    {"$inc": {"balance": -total_price}}
                )
                self.conn.order.update_one(
                    {"order_id": order_id},
                    {"$set": {"condition": "deliver"}}
                )
                if result.modified_count == 0:
                    return error.error_not_sufficient_funds(order_id)

            elif condition == "cancel":
                result = self.conn.user.update_one(
                    {"user_id": buyer_id},
                    {"$inc": {"balance": +total_price}}
                )
                self.conn.order.update_one(
                    {"order_id": order_id},
                    {"$set": {"condition": "cancel"}}
                )
                if result.modified_count == 0:
                    return error.error_funds(buyer_id)
            else:
                return error.error_repeat_pay(order_id)

        except errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def order_condition(self, order_id, will):
        try:
            order = self.conn.order.find_one({"order_id": order_id})
            if order is None:
                return error.error_invalid_order_id(order_id)

            if will == "receive":
                self.conn.order.update_one(
                    {"order_id": order_id},
                    {"$set": {"condition": will}}
                )

            elif will == "cancel":
                self.conn.order.update_one(
                    {"order_id": order_id},
                    {"$set": {"condition": will}}
                )
                book_id_list = order["book_id_list"]
                store_id = order["store_id"]
                for i in book_id_list:
                    count = self.conn.new_order_detail.find_one({"order_id": order_id,"book_id": i}).get("count")
                    self.conn.store.update_one(
                        {"store_id": store_id, "book_id": i, "stock_level": {"$gte": count}},
                        {"$inc": {"stock_level": + count}}
                    )

            else:

                return error.error_invalid_input(will)
        except errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def payment_seller(self, seller_id: str, order_id: str) -> (int, str):
        try:
            order = self.conn.order.find_one({"order_id": order_id})
            if order is None:
                return error.error_invalid_order_id(order_id)
            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            total_price = self.conn.order.find_one({"order_id": order_id}).get("total_price")
            condition = order["condition"]

            if condition == "receive":
                result = self.conn.user.update_one(
                    {"user_id": seller_id},
                    {"$inc": {"balance": +total_price}}
                )
                if result.modified_count == 0:
                    return error.error_funds(seller_id)

                self.conn.order.update_one(
                    {"order_id": order_id},
                    {"$set": {"condition": "close"}}
                )
            else:
                return error.error_buyer_not_receive(order_id)

        except errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except Exception as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def search_order(self,user_id):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            result = self.conn.order.find({"user_id": user_id})
            results = []
            for item in result:
                json_str = json.dumps(item, default=str)
                json_obj = json.loads(json_str)
                results.append(json_obj)
            return 200,  results
        except errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except Exception as e:
            return 530, "{}".format(str(e))
