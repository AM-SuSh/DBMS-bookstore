import pytest

from fe.access.buyer import Buyer
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.book import Book
import uuid

import time


class TestOrderCondition:
    seller_id: str
    store_id: str
    buyer_id: str
    password: str
    buy_book_info_list: [Book]
    total_price: int
    order_id: str
    buyer: Buyer
    now_time: float

    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_order_condition_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_order_condition_buyer_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_order_condition_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        self.now_time = time.time()
        gen_book = GenBook(self.seller_id, self.store_id)
        ok, buy_book_id_list = gen_book.gen(
            non_exist_book_id=False, low_stock_level=False, max_book_count=5
        )
        self.buy_book_info_list = gen_book.buy_book_info_list
        assert ok
        b = register_new_buyer(self.buyer_id, self.password)
        self.buyer = b
        code, self.order_id = b.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        self.total_price = 0
        for item in self.buy_book_info_list:
            book: Book = item[0]
            num = item[1]
            # book数据中不存在价格不存在的情况
            # if book.price is None:
            #    continue
            # else:
            self.total_price = self.total_price + book.price * num
        code = self.buyer.order_confirm(self.order_id, self.now_time, "confirm")
        assert code == 200
        code = self.buyer.add_funds(self.total_price)
        assert code == 200
        code = self.buyer.payment_buyer(self.order_id)
        assert code == 200

        yield

    # 用户取消订单
    def test_buyer_cancel_order_refund(self):
        code = self.buyer.order_condition(self.order_id, "cancel")
        assert code == 200

    # 订单收货
    def test_ok(self):
        code = self.buyer.order_condition(self.order_id, "receive")
        assert code == 200

    # 输入意愿字符非法
    def test_invalid_input(self):
        code = self.buyer.order_condition(self.order_id, "invalid")
        assert code != 200

    # 错误订单ID
    def test_error_order_id(self):
        code = self.buyer.order_condition(self.order_id + "_x", "receive")
        assert code != 200

    # 收货后查询历史订单
    def test_receive_search_order(self):
        code = self.buyer.order_condition(self.order_id, "receive")
        assert code == 200
        code, results = self.buyer.search_order(self.buyer_id)
        #for key, values in results[1][0].items():
        #    print(key,":",values,"\n")
        assert code == 200

    # 取消订单后查询历史订单
    def test_cancel_search_order(self):
        code = self.buyer.order_condition(self.order_id, "cancel")
        assert code == 200
        code, results = self.buyer.search_order(self.buyer_id)
        #for key, values in results[1][0].items():
        #    print(key,":",values,"\n")
        assert code == 200