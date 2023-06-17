from glob import glob

from django.test import TestCase

from nadoview import settings

from .epub import Epub
from .models import Book


class BookTestCast(TestCase):
    def setUp(self) -> None:
        pass
    def test_read_book(self):
        epubs = glob("/Users/ablegao/books/*.epub")
        for book in epubs:
            print(book)
            try:
                bookObj = Epub(book,settings.BOOK_PATH)
            except Exception:
                continue
            m = Book(
                book_id=bookObj.id,
                book_name=bookObj.book_name,
                book_author=bookObj.auther,
                language=bookObj.lang,
                )
            m.save()
            break



# Create your tests here.
