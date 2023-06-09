"""
URL configuration for nadoview project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

import book.views
from nadoview import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("book/upload_book",book.views.upload_book, name="upload_book"),
    path("book/refresh_book_cache",book.views.refresh_book_cache,name="refresh_book" ),
    path("book/book_hight",book.views.book_hight,name="hight"),
    path("book/book_light_remove",book.views.book_hight_remove,name="light_remove"),
    path("book/get_book_tag_cloud",book.views.get_book_tag_cloud,name="get_book_tag_cloud"),
    path("book/<str:id>/save_progress",book.views.book_save,name="book_update"),
    path("book/<str:id>", book.views.book),


    path("",  book.views.index),
    
]
urlpatterns+=static(settings.BOOK_URL,document_root=settings.BOOK_PATH)
urlpatterns+=static(settings.STATIC_URL,document_root=settings.BASE_DIR / "static")
