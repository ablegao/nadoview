import os

from django.http import HttpResponseRedirect, JsonResponse
from django.template import loader
from django.template.response import TemplateResponse
from genericpath import isfile

from nadoview import settings

from .epub import Epub
from .models import Book


# Create your views here.
def index(request):
    books = Book.objects.order_by("-last_read")
    # loader.get_template("book/index.html")
    return TemplateResponse(request,"book/index.html",{"books":books,"book_dir":settings.BOOK_URL})


def book(request,id=None):
   
    epub = Epub(os.path.join(settings.BOOK_PATH,id),settings.BOOK_PATH)
    
    book = Book.objects.get(book_id=id)
    epubcfi = ""
    if book.last_read_page is not None and book.last_read_page !="":
        epubcfi = book.last_read_page
        epubcfi = f'"{epubcfi}"'
    # if os.path.isdir(book) and len(root)==32:
    return TemplateResponse(request, "book/book.html",{"epub":epub,"book_model":book,"epubcfi":epubcfi,"book_dir":settings.BOOK_URL})


    # book = Epub(os.path.join(settings.BOOK_PATH,id))
    # try:
    #     Book.objects.get(book_id=book.id)
    # except Exception:
    #     pass
    
def book_save(request,id):
    obj = Book.objects.get(book_id=id)
    # print(obj)
    obj.last_read_page = request.POST.get("progress")
    obj.save()
    return JsonResponse({"msg":"success"})