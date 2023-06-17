from django.db import models


# Create your models here.
class Book(models.Model):
    book_id = models.CharField(max_length=32, primary_key=True)
    book_name = models.CharField(max_length=200)
    book_author = models.CharField(max_length=50)
    language = models.CharField(max_length=50)
    tags = models.TextField(null=True)
    last_read = models.DateTimeField(auto_now=True, auto_created=True)
    last_read_page = models.CharField(max_length=100)


