import os
from glob import glob

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
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

def upload_book(request):
    if request.method == "POST":
        file = request.FILES.get("uploadEpub")
        if file is None:
            return JsonResponse({"status":"error","msg":"no file"})
        if not file.name.endswith(".epub"):
            return JsonResponse({"status":"error","msg":"not epub file"})
        epub =  Epub(file,settings.BOOK_PATH,re_extract=True)

        # print(epub.book_name)
        if not Book.objects.filter(book_id=epub.id).exists():
            book = Book(book_id=epub.id,book_name=epub.book_name,book_author=epub.auther,language=epub.lang)
            book.save()
        return HttpResponseRedirect("/")
    return JsonResponse({"status":"error","msg":"not post"})
def refresh_book_cache(request):
    books = glob(os.path.join(settings.BOOK_PATH,"*"))
    for book in books:
        if isfile(book):
            continue
        epub = Epub(book,settings.BOOK_PATH)
        if not Book.objects.filter(book_id=epub.id).exists():
            book = Book(book_id=epub.id,book_name=epub.book_name,book_author=epub.auther,language=epub.lang)
            book.save()
    return JsonResponse({"msg":"success"})

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
    obj.last_read_index = request.POST.get("index")
    obj.total_page = request.POST.get("total_page")
    obj.save()
    return JsonResponse({"msg":"success"})