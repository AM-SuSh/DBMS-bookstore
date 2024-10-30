import pytest
from fe.access.buyer import Buyer
from fe.access.book import Book
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
import uuid
import time

class TestPaymentSeller:
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
        self.seller_id = "test_payment_seller_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_payment_seller_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_payment_seller_buyer_id_{}".format(str(uuid.uuid1()))
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
        code = self.buyer.payment_buyer(self.order_id)
        assert code == 200
        code = self.buyer.order_condition(self.order_id, "receive")
        assert code == 200
        yield

    # 错误订单ID
    def test_payment_seller_order_not_found(self):
        order_id = self.order_id + "_x"  # 修改 order_id
        code = self.buyer.payment_seller(self.seller_id, order_id)
        assert code != 200

    # 卖家ID不存在
    def test_payment_seller_not_exist(self):
        self.seller_id = self.seller_id + "_x"
        code = self.buyer.payment_seller(self.seller_id, self.order_id)
        assert code != 200

    # 买家未收货
    def test_not_received(self):
        code = self.buyer.order_condition(self.order_id, "cancel")
        assert code == 200
        code = self.buyer.payment_seller(self.seller_id, self.order_id)
        assert code != 200

    # 买家收货，卖家收款
    def test_ok(self):
        code = self.buyer.payment_seller(self.seller_id, self.order_id)
        assert code == 200

    # 收货后买家查询历史订单
    def test_search_order(self):
        code = self.buyer.payment_seller(self.seller_id, self.order_id)
        assert code == 200
        code, results = self.buyer.search_order(self.buyer_id)
        #for key,values in results[1][0].items():
        #    print(key,":",values,"\n")
        assert code == 200
