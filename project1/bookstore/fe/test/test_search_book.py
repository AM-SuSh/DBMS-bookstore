import time
import pytest
from be.model.search_book import BookSearch


class TestBookSearch:
    book_search: BookSearch

    @pytest.fixture(autouse=True)
    def setup(self):
        self.book_search = BookSearch()

    def test_normal_search_all(self):  # 正常情况下搜索全站图书
        query = "漫画"
        results = self.book_search.search_books(query)
        assert "results" in results
        assert "total_count" in results
        assert "per_page" in results
        found = False
        for item in results["results"]:
            if "book_info" in item:
                info = item["book_info"]
                if any(query in str(info.get(field)) for field in ['title', 'tags', 'book_intro', 'content']):
                    found = True
                    break
        assert found

        # Additional check to ensure total_count is reasonable
        assert results["total_count"] >= 0

        # Check if per_page is set correctly if not provided
        assert results["per_page"] == 10 if not results["per_page"] else True


    def test_empty_query(self):  # 测试空查询，显示结果数量为零
        query = " "
        results = self.book_search.search_books(query)
        assert "results" in results
        assert "total_count" in results
        assert "per_page" in results
        # 可能预期空查询时返回空结果或特定的提示信息
        assert results["total_count"] == 0


    def test_special_char_query(self):  # 测试特殊字符
        query = "!@#$%^&*()"
        results = self.book_search.search_books(query)
        assert "results" in results
        assert "total_count" in results
        assert "per_page" in results
        # 根据实际情况判断特殊字符查询的结果是否符合预期
        assert results["total_count"] == 0


    def test_tags_scope(self):# 测试不同范围搜索（tags）
        query = "儿童"
        scope = 'tags'
        results = self.book_search.search_books(query, search_scope=scope)
        assert "results" in results
        assert "total_count" in results
        assert "per_page" in results
        for item in results["results"]:
            assert any(query in tag for tag in item["book_info"]["tags"]) if "book_info" in item and "tags" in item[
                "book_info"] else False


    def test_book_intro_scope(self):# 测试不同范围搜索（book_intro）
        query = "漫画"
        scope = 'book_intro'
        results = self.book_search.search_books(query, search_scope=scope)
        assert "results" in results
        assert "total_count" in results
        assert "per_page" in results
        for item in results["results"]:
            assert query in item["book_info"]["book_intro"] if "book_info" in item and "book_intro" in item[
                "book_info"] else False


    def test_no_results(self):#不会被搜索到的情况
        query = "一个非常罕见几乎不可能存在的关键词"
        scope = 'content'
        results = self.book_search.search_books(query, search_scope=scope)
        assert "results" in results
        assert "total_count" in results
        assert "per_page" in results
        assert len(results["results"]) == 0
        assert results["total_count"] == 0


    def test_store_id_filtering(self):  # 测试商店 ID 过滤
        # 传入不同的商店 ID，验证结果是否正确过滤了商店。
        query = "传记"
        store_id = "test_add_book_stock_level1_store_df28f743-9664-11ef-8dc7-20c19b178616"
        results = self.book_search.search_books(query, store_id=store_id)
        assert "results" in results
        assert "total_count" in results
        assert "per_page" in results
        # 检查结果中的商店 ID 是否都与传入的商店 ID 一致
        for item in results["results"]:
            assert item["store_id"] == store_id if "store_id" in item else False


    def test_nonexistent_store_id(self):#测试商店 ID 不存在的情况
        query = "41652965952"
        store_id = "一个不存在的商店 ID"
        results = self.book_search.search_books(query, store_id=store_id)
        assert "results" in results
        assert results["results"] == []
        assert "total_count" in results
        assert results["total_count"] == 0
        assert "per_page" in results
        assert results["per_page"] == 10


    def test_pagination(self):  # 分页功能
        query = "test query"
        per_page = 5
        results = self.book_search.search_books(query, per_page=per_page)
        assert "results" in results
        assert "total_count" in results
        assert "per_page" in results
        assert len(results["results"]) <= per_page


    def test_per_page_variations(self):#测试不同每页条数的情况
        query = "示例"
        scope = None
        store_id = None
        for per_page_value in [5, 15, 20]:
            results = self.book_search.search_books(query, search_scope=scope, store_id=store_id,
                                                    per_page=per_page_value)
            assert "results" in results
            assert "total_count" in results
            assert "per_page" in results
            assert len(results["results"]) <= per_page_value


    def test_response_time(self):  # 响应时间小于1s
        query = "test query"
        start_time = time.time()
        results = self.book_search.search_books(query)
        end_time = time.time()
        response_time = end_time - start_time
        assert response_time < 1  # 假设响应时间应小于 1 秒
