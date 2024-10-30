import pytest

from fe.access.buyer import Buyer
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.book import Book
import uuid

import time


class TestPaymentBuyer:
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
        self.seller_id = "test_payment_buyer_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_payment_buyer_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_payment_buyer_buyer_id_{}".format(str(uuid.uuid1()))
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
        code = self.buyer.add_funds(self.total_price)
        assert code == 200
        code = self.buyer.order_confirm(self.order_id, self.now_time, "confirm")
        assert code == 200
        yield

    # 买家付款
    def test_ok_payment_buyer(self):
        code = self.buyer.payment_buyer(self.order_id)
        assert code == 200

    # 错误用户，付款失败
    def test_error_user_id_payment_buyer(self):
        self.buyer.user_id = self.buyer.user_id + "_x"
        code = self.buyer.payment_buyer(self.order_id)
        assert code != 200

    # 错误密码，付款失败
    def test_error_password_payment_buyer(self):
        self.buyer.password = self.buyer.password + "_x"
        code = self.buyer.payment_buyer(self.order_id)
        assert code != 200

    # 错误订单付款失败
    def test_error_order_id_payment_buyer(self):
        code = self.buyer.payment_buyer(self.order_id + "_x")
        assert code != 200

    # 取消订单，退款买家
    def test_cancel_order_payment_buyer(self):
        code = self.buyer.payment_buyer(self.order_id)
        assert code == 200
        code = self.buyer.order_condition(self.order_id, "cancel")
        assert code == 200
        code = self.buyer.payment_buyer(self.order_id)
        assert code == 200

    # 账户余额不足，付款失败
    def test_balance_short_payment_buyer(self):
        code = self.buyer.add_funds(- self.total_price)
        assert code == 200
        code = self.buyer.payment_buyer(self.order_id)
        assert code != 200

    # 重复支付失败
    def test_repeat_pay(self):
        code = self.buyer.payment_buyer(self.order_id)
        assert code == 200
        code = self.buyer.payment_buyer(self.order_id)
        assert code != 200

    # 付款成功（发货）查询订单
    def test_cancel_search_order(self):
        code = self.buyer.payment_buyer(self.order_id)
        assert code == 200
        code, results = self.buyer.search_order(self.buyer_id)
        #for key, values in results[1][0].items():
        #    print(key,":",values,"\n")
        assert code == 200