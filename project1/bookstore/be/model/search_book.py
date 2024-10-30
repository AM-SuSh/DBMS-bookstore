import json
import logging
from pymongo import MongoClient, errors, TEXT


class BookSearch:
    def __init__(self, db_uri='mongodb://localhost:27017/', db_name='bookstore'):

        self.client = MongoClient(db_uri)
        self.db = self.client[db_name]
        self.store_collection = self.db["store"]
        # 删除可能已存在的manh旧索引
        #try:
            #self.store_collection.drop_index("book_info_text_index")
        #except errors.OperationFailure:
            #pass

        # 创建新的索引
        self.store_collection.create_index([
            ("book_info.tags", TEXT),
            ("book_info.title", TEXT),
            ("book_info.book_intro", TEXT),
            ("book_info.content", TEXT)
        ], name="book_info_text_index")

        all_books = self.store_collection.find()
        for book in all_books:
            if isinstance(book['book_info'], dict):
                continue
            self.store_collection.update_one({'_id':book['_id']},{"$set":{"book_info":json.loads(book['book_info'])}})

    def search_books(self, query, search_scope=None, store_id=None, per_page=None):
        try:
            search_filter = {}
            if query:
                if search_scope == 'title':
                    search_filter["$text"] = {"$search": query, "$caseSensitive": False, "$diacriticSensitive": False}
                    search_filter["book_info.title"] = {"$regex": query, "$options": "i"}
                elif search_scope == 'tags':
                    search_filter["$text"] = {"$search": query, "$caseSensitive": False, "$diacriticSensitive": False}
                    search_filter["book_info.tags"] = {"$regex": query, "$options": "i"}
                elif search_scope == 'book_intro':
                    search_filter["$text"] = {"$search": query, "$caseSensitive": False, "$diacriticSensitive": False}
                    search_filter["book_info.book_intro"] = {"$regex": query, "$options": "i"}
                elif search_scope == 'content':
                    search_filter["$text"] = {"$search": query, "$caseSensitive": False, "$diacriticSensitive": False}
                    search_filter["book_info.content"] = {"$regex": query, "$options": "i"}
                else:
                    search_filter["$text"] = {"$search": query}
            if store_id:
                search_filter["store_id"] = store_id

            # 使用游标获取所有结果
            cursor = self.store_collection.find(search_filter)
            total_count = self.store_collection.count_documents(search_filter)
            if not per_page:
                per_page = 10  # 默认每页条数

            results = []
            for item in cursor:
                json_str = json.dumps(item,default=str)
                json_obj = json.loads(json_str)
                results.append(json_obj)

            return {
                "results": results,
                "total_count": total_count,
                "per_page": per_page
            }
        except errors.PyMongoError as e:
            logging.error(f"Database error: {str(e)}")
            return {"results": [], "total_count": 0, "per_page": per_page}


# if __name__ == '__main__':
#    book_search = BookSearch()
#    query = input("请输入要搜索的关键字: ")
#    search_scope = input("请输入搜索范围（tags/title/book_intro/content/all）: ") or None
#    store_id = input("请输入商店 ID（可选）: ") or None
#    per_page_input = input("请输入每页想要显示的条数（不输入则默认为 10）：")
#    per_page = int(per_page_input) if per_page_input else None
#    results = book_search.search_books(query, search_scope, store_id, per_page)
#    print("搜索结果:", json.dumps(results, ensure_ascii=False, indent=2))