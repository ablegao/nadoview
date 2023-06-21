import datetime
import hashlib
import os
import os.path
import shutil
import traceback
import xml.etree.ElementTree as ET
import xml.sax as sax  # import ContentHandler
import zipfile
from collections.abc import Iterable
from glob import glob
from urllib.parse import unquote
from xml.dom import minidom

from PIL import Image


class ContainerHandler(sax.ContentHandler):
    def __init__(self):
        self.path = ''

    def startElement(self, name, attrs):
        if name == 'rootfile':
            self.path = attrs['full-path']


class Epub:
    zip = None

    def __init__(self, file: str, cache_path=None,re_extract=False) -> None:
        self.book_name = ""
        self.auther = ""
        self.id = ""
        self.book_url = ""
        self.tags = ""
        self.lang = ""
        self.manifest = {}
        self.cover_path = ""
        self.spine = []
        self.menu = []
        self.re_extract = re_extract

        self.cache_path = cache_path

        if zipfile.is_zipfile(file):
            self.zip_file = file
            self.init_epub(file)
        elif os.path.isdir(file):
            self.init_dir(file)

    def relative_path(self, file):
        return file[len(self.book_url) + 1:]

    def init_epub(self, path):
        '''
        解压 epub 文件到cache_path 
        '''

        # 读取epub 文件中content_opf 中的配置信息,来获取图书名字
        with zipfile.ZipFile(path, "r") as zip:
            conttainer = ContainerHandler()
            sax.parse(zip.open("META-INF/container.xml"), conttainer)
            doc = minidom.parse(zip.open(conttainer.path))
            metadata = doc.getElementsByTagName("metadata")[0]
            title = metadata.getElementsByTagName("dc:title")[0].firstChild.data
            self.book_name = title
            name = hashlib.md5()
            name.update(self.book_name.encode('utf-8'))
            self.id = name.hexdigest()
            if self.cache_path and not os.path.exists(self.cache_path):
                os.makedirs(self.cache_path)
            path = os.path.join(self.cache_path, self.id)
            if os.path.exists(path) and self.re_extract and len(self.id)==32:
                shutil.rmtree(path)
            zip.extractall(path)
            self.init_dir(path)

    def init_dir(self, path):
        self.book_url = path
        conttainer = ContainerHandler()
        sax.parse(os.path.join(self.book_url, "META-INF/container.xml"), conttainer)
        self.opf_file = os.path.join(self.book_url, conttainer.path)
        self.opf_base = os.path.dirname(self.opf_file)
        with open(self.opf_file, "rb") as opf:
            self.parse_opf(opf)
        self.opf_file = self.relative_path(self.opf_file)
        # async with Session() as session:
        #     book = await session.query(Book).filter(Book.id == self.id).first()
        #     if book:
        #         book.last_read_time = datetime.datetime.now()
        #     else:
        #         book = Book(id=self.id,
        #                     book_name=self.book_name,
        #                     book_url=self.book_url,
        #                     tags=self.tags,
        #                     lang=self.lang,
        #                     book_image=self.cover_path,
        #                     last_read_index=0,
        #                     last_read_scroll_number=0,
        #                     last_read_time=datetime.datetime.now(),
        #                     )
        #         session.add(book)
        #     session.commit()

    def parse_opf(self, opf_reader):
        # self.opf_dir = os.path.join(self.book_url, conttainer.path)
        doc = minidom.parse(opf_reader)
        self.parse_metadata(doc)
        self.parse_mainfest(doc)
        self.parse_spine(doc)
        self.parse_menu()
        self.parse_cover(doc)

    def read(self, file):
        # return self.zip.open(file)
        with open(os.path.join(self.opf_base, file), "r") as data:
            return data.read()
        # return open(os.path.join(self.opf_base, file), "r")

    def book_file(self, file):
        return os.path.join(self.opf_base, file)

    def file_exists(self, file):
        # return file in self.zip.namelist()
        return os.path.exists(os.path.join(self.opf_base, file))

    def url_by_id(self, id):
        file = self.manifest[id]["href"]
        file = os.path.abspath(os.path.join(self.opf_base, file))
        return file

    def read_by_id(self, id):
        file = self.url_by_id(id)
        return file

    def parse_menu(self):
        if "ncx" in self.manifest:
            ncx_file = self.manifest["ncx"]
            doc = minidom.parse(self.book_file(ncx_file["href"]))
            # 分析 ncx 文件, navPoint 中的text字段，和content
            navMap = doc.getElementsByTagName("navMap")
            if navMap is not None:
                for navPoint in navMap[0].getElementsByTagName("navPoint"):
                    try:
                        self.menu.append({
                            "text": navPoint.getElementsByTagName("text")[0].firstChild.data,
                            "src": navPoint.getElementsByTagName("content")[0].getAttribute("src"),
                        })
                    except Exception as e:
                        pass
            return
        if "nav" in self.manifest:
            nav_file = self.manifest["nav"]
            doc = minidom.parse(self.book_file(nav_file["href"]))
            # 分析 ncx 文件, navPoint 中的text字段，和content
            navMap = doc.getElementsByTagName("ol")
            if navMap is not None:
                for navPoint in navMap[0].getElementsByTagName("li"):
                    try:
                        self.menu.append({
                            "text": navPoint.getElementsByTagName("a")[0].firstChild.data,
                            "src": navPoint.getElementsByTagName("a")[0].getAttribute("href"),
                        })
                    except Exception as e:
                        pass
            return

    def parse_metadata(self, doc):
        metadata = doc.getElementsByTagName("metadata")
        if metadata is not None:
            metadata = metadata[0]
            title = metadata.getElementsByTagName("dc:title")
            if title and title[0].firstChild:
                self.book_name = title[0].firstChild.data
            creator = metadata.getElementsByTagName("dc:creator")
            if creator and creator[0].firstChild:
                self.auther = creator[0].firstChild.data

            lang = metadata.getElementsByTagName("dc:language")
            if lang and lang[0].firstChild:
                self.lang = lang[0].firstChild.data

            name = hashlib.md5()
            name.update(self.book_name.encode('utf-8'))
            self.id = name.hexdigest()

    def parse_cover(self, doc: minidom.Document):
        cover_path = os.path.join(self.book_url, self.id + ".jpg")
        if os.path.exists(cover_path):
            self.cover_path = cover_path
            return

        if "cover" in self.manifest:
            self.cover_path = self.manifest["cover"]["href"]
            print(self.cover_path)
        else:
            metas = doc.getElementsByTagName("meta")
            for meta in metas:
                if meta.getAttribute("name") == "cover":
                    id = meta.getAttribute("content")
                    self.cover_path = unquote(self.manifest[id]["href"])
                    break
        cover = os.path.join(self.opf_base, self.cover_path)
        try:
            Image.open(cover).save(cover_path)
            self.cover_path = cover_path
        except Exception as e:
            print("ERROR:.......... cover",e)

    def parse_mainfest(self, doc):
        manifest = doc.getElementsByTagName("manifest")
        if manifest is not None:
            for item in manifest[0].getElementsByTagName("item"):
                id = item.getAttribute("id")
                self.manifest[id] = {
                    "id": id,
                    "href": item.getAttribute("href"),
                    "media-type": item.getAttribute("media-type"),
                }

    def parse_spine(self, doc):
        spine = doc.getElementsByTagName("spine")
        if spine is not None:
            for item in spine[0].getElementsByTagName("itemref"):
                self.spine.append({
                    "id": item.getAttribute("idref"),
                    "linear": item.getAttribute("linear"),
                    "href": self.manifest[item.getAttribute("idref")]["href"],
                })

    def get_chapter_url_by_index(self, index):
        if index < 0 or index >= len(self.spine):
            return None
        self.current_index = index
        # with Session() as session:
        #     book = session.query(Book).filter(Book.id == self.id).first()
        #     book.last_read_index = index
        #     book.last_read_time = datetime.datetime.now()
        #     session.commit()
        return self.url_by_id(self.spine[index]["id"])

    def get_next_chapter_url(self):
        return self.get_chapter_url_by_index(self.current_index + 1)

    def get_priv_chapter_url(self):
        return self.get_chapter_url_by_index(self.current_index - 1)

    def __del__(self) -> None:
        if self.zip is not None:
            self.zip.close()
            # print("free", self.book_url)
