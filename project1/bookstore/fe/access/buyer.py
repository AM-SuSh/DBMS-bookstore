import requests
from urllib.parse import urljoin
from fe.access.auth import Auth


class Buyer:
    def __init__(self, url_prefix, user_id, password):
        self.url_prefix = urljoin(url_prefix, "buyer/")
        self.user_id = user_id
        self.password = password
        self.token = ""
        self.terminal = "my terminal"
        self.auth = Auth(url_prefix)
        code, self.token = self.auth.login(self.user_id, self.password, self.terminal)
        assert code == 200

    def new_order(self, store_id: str, book_id_and_count: [(str, int)]) -> (int, str):
        books = []
        for id_count_pair in book_id_and_count:
            books.append({"id": id_count_pair[0], "count": id_count_pair[1]})
        json = {"user_id": self.user_id, "store_id": store_id, "books": books}
        # print(simplejson.dumps(json))
        url = urljoin(self.url_prefix, "new_order")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        response_json = r.json()
        return r.status_code, response_json.get("order_id")

    def payment(self, order_id: str):
        json = {
            "user_id": self.user_id,
            "password": self.password,
            "order_id": order_id,
        }
        url = urljoin(self.url_prefix, "payment")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def add_funds(self, add_value: str) -> int:
        json = {
            "user_id": self.user_id,
            "password": self.password,
            "add_value": add_value,
        }
        url = urljoin(self.url_prefix, "add_funds")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def order_confirm(self, order_id: str, now_time: float, will: str):
        json = {
            "user_id": self.user_id,
            "password": self.password,
            "order_id": order_id,
            "now_time": now_time,
            "will": will,
        }
        url = urljoin(self.url_prefix, "order_confirm")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        #print(f"Request body: {r.request.body}")
        return r.status_code

    def payment_buyer(self, order_id: str):
        json = {
            "user_id": self.user_id,
            "password": self.password,
            "order_id": order_id
        }
        url = urljoin(self.url_prefix, "payment_buyer")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def order_condition(self, order_id: str, will: str):
        json = {
            "order_id": order_id,
            "will": will
        }
        url = urljoin(self.url_prefix, "order_condition")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def payment_seller(self, seller_id: str, order_id: str):
        json = {
            "order_id": order_id,
            "seller_id": seller_id
        }
        url = urljoin(self.url_prefix, "payment_seller")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def search_order(self, user_id: str):
        json = {"user_id": user_id}
        url = urljoin(self.url_prefix, "search_order")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        if r.status_code == 200:
            return r.status_code, r.json()

