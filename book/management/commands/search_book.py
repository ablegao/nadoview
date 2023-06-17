from glob import glob

from django.core.management.base import BaseCommand, CommandError

from book.epub import Epub
from book.models import Book
from nadoview import settings


class Command(BaseCommand):
    help = "search books"
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument("dir", nargs="+", type=str)

    def handle(self, *args, **options):
        print(options)
        epubs = glob(options["dir"][1])
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
            # break