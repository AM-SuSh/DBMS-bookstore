import os
import sqlite3 as sqlite
import random
import base64
import simplejson as json
from pymongo import MongoClient
from fe import conf
class Book:
    id: str
    title: str
    author: str
    publisher: str
    original_title: str
    translator: str
    pub_year: str
    pages: int
    price: int
    currency_unit: str
    binding: str
    isbn: str
    author_intro: str
    book_intro: str
    content: str
    tags: [str]
    pictures: [bytes]

    def __init__(self):
        self.tags = []
        self.pictures = []


class BookDB:
    def __init__(self, large: bool = False):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['bookstore']
        self.collection = self.db['books']

    def get_book_count(self):
        count = self.collection.count_documents({})
        return count

    def get_book_info(self, start, size) -> list[Book]:
        books = []

        cursor = self.collection.find({}).sort('id').skip(start).limit(size)

        for row in cursor:
            book = Book()
            book.id = row.get('id')
            book.title = row.get('title')
            book.author = row.get('author')
            book.publisher = row.get('publisher')
            book.original_title = row.get('original_title')
            book.translator = row.get('translator')
            book.pub_year = row.get('pub_year')
            book.pages = row.get('pages')
            book.price = row.get('price')
            book.currency_unit = row.get('currency_unit')
            book.binding = row.get('binding')
            book.isbn = row.get('isbn')
            book.author_intro = row.get('author_intro')
            book.book_intro = row.get('book_intro')
            book.content = row.get('content')
            tags = row.get('tags', '')
            picture = row.get('picture')

            for tag in tags.split("\n"):
                if tag.strip() != "":
                    book.tags.append(tag)
            '''
            for i in range(0, random.randint(0, 9)):
                if picture is not None:
                    encode_str = base64.b64encode(picture).decode("utf-8")
                    book.pictures.append(encode_str)
            '''
            books.append(book)

        return books


if __name__ == "__main__":
    book_db = BookDB(conf.Use_Large_DB)
    print(book_db.get_book_count())
    books = book_db.get_book_info(0, 5)
    print(f"Number of books retrieved: {len(books)}")
    for book in books:
        print(book.title, book.author)
