import pytest

from fe.access.buyer import Buyer
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.book import Book
import uuid

import time


class TestOrderConfirm:
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
        self.seller_id = "test_order_confirm_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_order_confirm_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_order_confirm_buyer_id_{}".format(str(uuid.uuid1()))
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
        yield

    # 确认订单
    def test_confirm_order(self):
        code = self.buyer.order_confirm(self.order_id, self.now_time, "confirm")
        assert code == 200

    # 取消订单
    def test_cancel_order(self):
        code = self.buyer.order_confirm(self.order_id, self.now_time, "cancel")
        assert code == 200

    # 超时确认订单
    def test_overtime_confirm_order(self):
        code = self.buyer.order_confirm(self.order_id, self.now_time + 1000, "confirm")
        assert code == 200

    # 意愿输入字符非法
    def test_invalid_input_order_confirm(self):
        code = self.buyer.order_confirm(self.order_id, self.now_time, "invalid")
        assert code != 200

    # 错误订单
    def test_error_order_confirm(self):
        self.order_id = self.order_id + "_x"
        code = self.buyer.order_confirm(self.order_id, self.now_time, "confirm")
        assert code != 200

    # 确认订单后查询历史订单
    def test_search_order(self):
        code = self.buyer.order_confirm(self.order_id, self.now_time, "confirm")
        assert code == 200
        code, results = self.buyer.search_order(self.buyer_id)
        #for key, values in results[1][0].items():
        #    print(key,":",values,"\n")
        assert code == 200
