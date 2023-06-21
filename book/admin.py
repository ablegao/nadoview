from django.contrib import admin

from book.models import Book

# Register your models here.

class BookAdmin(admin.ModelAdmin):
    list_display=["book_id","book_name","book_author","tags","language","last_read"]
    list_filter = ["language"]
    search_fields = ["book_name","book_author","tags"]
    ordering =["last_read"]

admin.site.register(Book,BookAdmin)