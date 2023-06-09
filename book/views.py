import json
import os
import re
from glob import glob

from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.template.response import TemplateResponse
from genericpath import isfile

from nadoview import settings

from .epub import Epub
from .models import Book, BookHighlight


# Create your views here.
def index(request):
    books = Book.objects.order_by("-last_read")
    # loader.get_template("book/index.html")
    if request.GET.get("format") == "json":
        return HttpResponse(serializers.serialize("json",books),content_type="application/json")
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

    hights = BookHighlight.objects.filter(book_id=id)

    # if os.path.isdir(book) and len(root)==32:
    return TemplateResponse(request, "book/book_scrolled.html",{"epub":epub,"hights":hights,"book":book,"epubcfi":epubcfi,"book_dir":settings.BOOK_URL})


    # book = Epub(os.path.join(settings.BOOK_PATH,id))
    # try:
    #     Book.objects.get(book_id=book.id)
    # except Exception:
    #     pass

def get_book_tag_cloud(request):
    books = Book.objects.all()
    tags = {}
    for book in books:
        # if book.book_author and book.book_author != "":
        #     book.book_author = book.book_author.replace("，",",")
        #     for auther in book.book_author.split(","):
        #         if auther in tags:
        #             tags[auther] += 1
        #         else:
        #             tags[auther] = 1
        if book.tags and book.tags != "":
            book.tags = book.tags.replace("，",",")
            for tag in book.tags.split(","):
                if tag in tags:
                    tags[tag] += 1
                else:
                    tags[tag] = 1
        
    out = []
    for k,v in tags.items():
        out.append({"tag_name":k,"tag_count":v})
    return  JsonResponse({"tag_cloud":out}) #HttpResponse(json.dumps(out),content_type="application/json")
def book_save(request,id):
    obj = Book.objects.get(book_id=id)
    print(request.POST)
    # print(obj)
    obj.last_read_page = request.POST.get("progress")
    obj.last_read_index = request.POST.get("index")
    obj.total_page = request.POST.get("total_page")
    obj.save()
    return JsonResponse({"msg":"success"})


def book_hight(request):
    try:
        obj = BookHighlight.objects.get(book_id=request.POST.get("book_id"),
                                    epubcfi=request.POST.get("cfi"),
                                    method_name = request.POST.get("method_name")
                                    )
        obj.remark = request.POST.get("remark")
        if request.POST.get("delete","") == "true":
            obj.delete();
            return JsonResponse({"msg":"success"})
        else:
            return JsonResponse({"error":"exists"})
    except BookHighlight.DoesNotExist:
        if request.POST.get("delete","") == "true":
            return JsonResponse({"msg":"not exists"})
             
        obj = BookHighlight(book_id=request.POST.get("book_id"),
                            epubcfi=request.POST.get("cfi"),
                            method_name = request.POST.get("method_name"),
                            remark = request.POST.get("remark"),
                            )
        obj.save();

    return JsonResponse({"msg":"success"})


def book_hight_remove(request):
    try:
        obj = BookHighlight.objects.filter(book_id=request.POST.get("book_id"),
                                    epubcfi=request.POST.get("cfi")
                                    )
        obj.delete()
        return JsonResponse({"msg":"success"})
    except BookHighlight.DoesNotExist:
        return JsonResponse({"msg":"not exists"})