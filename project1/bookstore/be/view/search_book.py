from flask import Flask, request, jsonify
from be.model.search_book import BookSearch

app = Flask(__name__)
book_search = BookSearch()


@app.route('/search_books', methods=['POST'])
def search_books_api():
    query = request.args.get('query')
    search_scope = request.args.get('search_scope')
    store_id = request.args.get('store_id')
    per_page_input = request.args.get('per_page')
    per_page = int(per_page_input) if per_page_input else None

    results = book_search.search_books(query, search_scope, store_id, per_page)
    return jsonify(results), 200
