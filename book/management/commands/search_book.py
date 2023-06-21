import os
from glob import glob

import boto3
from django.core.management.base import BaseCommand, CommandError

from book.epub import Epub
from book.models import Book
from nadoview import settings

s3 = boto3.client('s3')

class Command(BaseCommand):
    help = "search books"
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument("dir", nargs="+", type=str)

    def handle(self, *args, **options):
  
        epubs = glob(options["dir"][1])
        for book in epubs:
            print(book)
            try:
                bookObj = Epub(book,settings.BOOK_PATH)
                s3.upload_file(book,"nadoviewbooks",f"{bookObj.id}.epub",ExtraArgs={'ACL': 'public-read',"ContentType":"application/epub+zip"})
                if bookObj.cover_path != "" and os.path.exists(bookObj.cover_path):
                    s3.upload_file(bookObj.cover_path,"nadoviewbooks",os.path.basename(bookObj.cover_path),ExtraArgs={'ACL': 'public-read',"ContentType":"image/jpeg"})
            except Exception:
                continue
            # m = Book(
            #     book_id=bookObj.id,
            #     book_name=bookObj.book_name,
            #     book_author=bookObj.auther,
            #     language=bookObj.lang,
            #     )
            # m.save()
            # break