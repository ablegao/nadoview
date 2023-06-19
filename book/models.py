import os

from django.db import models

from nadoview import settings


# Create your models here.
class Book(models.Model):
    book_id = models.CharField(max_length=32, primary_key=True)
    book_name = models.CharField(max_length=200)
    book_author = models.CharField(max_length=50)
    language = models.CharField(max_length=50)
    tags = models.TextField(null=True)
    last_read = models.DateTimeField(auto_now=True, auto_created=True)
    last_read_page = models.CharField(max_length=100)
    last_read_index = models.IntegerField(default=0)
    total_page = models.IntegerField(default=0)

    @property
    def icon_exists(self):
        if os.path.exists(os.path.join(settings.BOOK_PATH,self.book_id,f"{self.book_id}.jpg")):
            return True
        return False
    
    # def __dict__(self):



