from django.contrib import admin

from book.models import Book

# Register your models here.

class BookAdmin(admin.ModelAdmin):
    list_display=["book_id","book_name","book_author","tags","language"]
    list_filter = ["language"]
    search_fields = ["book_name","book_author","tags"]
admin.site.register(Book,BookAdmin)