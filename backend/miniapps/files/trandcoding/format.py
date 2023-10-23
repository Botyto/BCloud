from typing import List, Tuple

ALL_CATEGORIES: List["Category"] = []


class Category:
    name: str

    def __init__(self, name: str):
        self.name = name
        ALL_CATEGORIES.append(self)

ALL_FORMATS: List["Format"] = []


class Format:
    mime: str
    category: Category
    extensions: Tuple[str, ...]

    def __init__(self, mime: str, category: Category, *extensions: str):
        self.mime = mime
        self.category = category
        self.extensions = extensions
        ALL_FORMATS.append(self)

    def __repr__(self):
        return f"Format({self.mime}, {self.category}, {','.join(self.extensions)})"
    
    @classmethod
    def all(cls):
        return ALL_FORMATS
    
    @classmethod
    def by_category(cls, category: Category):
        return [f for f in ALL_FORMATS if f.category == category]
    
    @classmethod
    def by_ext(cls, ext: str):
        return next(f for f in ALL_FORMATS if ext in f.extensions)
    
    @classmethod
    def by_mime(cls, mime: str):
        return next(f for f in ALL_FORMATS if f.mime == mime)

CATEGORY_IMAGE = Category("image")
IMAGE_BMP = Format("image/bmp", CATEGORY_IMAGE, ".bmp")
IMAGE_DDS = Format("image/dds", CATEGORY_IMAGE, ".dds")
IMAGE_GIF = Format("image/gif", CATEGORY_IMAGE, ".gif")
IMAGE_ICO = Format("image/x-icon", CATEGORY_IMAGE, ".ico")
IMAGE_JPEG = Format("image/jpeg", CATEGORY_IMAGE, ".jpg", ".jpeg")
IMAGE_JPEG2000 = Format("image/jp2", CATEGORY_IMAGE, ".jp2", ".j2k", ".jpx", ".jpm", ".mj2")
IMAGE_PNG = Format("image/png", CATEGORY_IMAGE, ".png")
IMAGE_PPM = Format("image/ppm", CATEGORY_IMAGE, ".ppm")
IMAGE_TGA = Format("image/tga", CATEGORY_IMAGE, ".tga")
IMAGE_TIFF = Format("image/tiff", CATEGORY_IMAGE, ".tif", ".tiff")
IMAGE_WEBP = Format("image/webp", CATEGORY_IMAGE, ".webp")
IMAGE_CUR = Format("image/x-cur", CATEGORY_IMAGE, ".cur")
IMAGE_PIXAR = Format("image/x-pixar", CATEGORY_IMAGE, ".pxr")
IMAGE_PSD = Format("image/vnd.adobe.photoshop", CATEGORY_IMAGE, ".psd")
IMAGE_SVG = Format("image/svg+xml", CATEGORY_IMAGE, ".svg")

CATEGORY_DOCUMENT = Category("document")
DOCUMENT_TXT = Format("text/plain", CATEGORY_DOCUMENT, ".txt")
DOCUMENT_PDF = Format("application/pdf", CATEGORY_DOCUMENT, ".pdf")
DOCUMENT_DOC = Format("application/msword", CATEGORY_DOCUMENT, ".doc")
DOCUMENT_DOCX = Format("application/vnd.openxmlformats-officedocument.wordprocessingml.document", CATEGORY_DOCUMENT, ".docx")
DOCUMENT_RTF = Format("application/rtf", CATEGORY_DOCUMENT, ".rtf")
DOCUMENT_ODT = Format("application/vnd.oasis.opendocument.text", CATEGORY_DOCUMENT, ".odt", ".fodt")

CATEGORY_EBOOK = Category("ebook")
EBOOK_EPUB = Format("application/epub+zip", CATEGORY_EBOOK, ".epub")
EBOOK_MOBI = Format("application/x-mobipocket-ebook", CATEGORY_EBOOK, ".mobi")
EBOOK_AZW = Format("application/vnd.amazon.mobi8-ebook", CATEGORY_EBOOK, ".azw")
EBOOK_AZW3 = Format("application/vnd.amazon.mobi8-ebook", CATEGORY_EBOOK, ".azw3")
EBOOK_AZW4 = Format("application/vnd.amazon.ebook", CATEGORY_EBOOK, ".azw4")

CATEGORY_VIDEO = Category("video")
VIDEO_MP4 = Format("video/mp4", CATEGORY_VIDEO, ".mp4")
VIDEO_WEBM = Format("video/webm", CATEGORY_VIDEO, ".webm")
VIDEO_MKV = Format("video/x-matroska", CATEGORY_VIDEO, ".mkv")
VIDEO_AVI = Format("video/x-msvideo", CATEGORY_VIDEO, ".avi")
VIDEO_MOV = Format("video/quicktime", CATEGORY_VIDEO, ".mov")
VIDEO_MPEG = Format("video/mpeg", CATEGORY_VIDEO, ".mpeg", ".mpg")
VIDEO_FLV = Format("video/x-flv", CATEGORY_VIDEO, ".flv")

CATEGORY_TABLE = Category("table")
TABLE_CSV = Format("text/csv", CATEGORY_TABLE, ".csv")
TABLE_XLS = Format("application/vnd.ms-excel", CATEGORY_TABLE, ".xls")
TABLE_XLSX = Format("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", CATEGORY_TABLE, ".xlsx")
TABLE_ODS = Format("application/vnd.oasis.opendocument.spreadsheet", CATEGORY_TABLE, ".ods")

CATEGORY_XML = Category("xml")
XML_XML = Format("text/xml", CATEGORY_XML, ".xml")
XML_HTML = Format("text/html", CATEGORY_XML, ".html", ".htm")
XML_RSS = Format("application/rss+xml", CATEGORY_XML, ".rss")

CATEGORY_ARCHIVE = Category("archive")
ARCHIVE_ZIP = Format("application/zip", CATEGORY_ARCHIVE, ".zip")
ARCHIVE_RAR = Format("application/x-rar-compressed", CATEGORY_ARCHIVE, ".rar")
ARCHIVE_7Z = Format("application/x-7z-compressed", CATEGORY_ARCHIVE, ".7z")
ARCHIVE_TAR = Format("application/x-tar", CATEGORY_ARCHIVE, ".tar")
ARCHIVE_GZ = Format("application/gzip", CATEGORY_ARCHIVE, ".gz")
ARCHIVE_BZ2 = Format("application/x-bzip2", CATEGORY_ARCHIVE, ".bz2")
ARCHIVE_TAR_GZ = Format("application/x-gzip", CATEGORY_ARCHIVE, ".tar.gz")
ARCHIVE_TAR_BZ2 = Format("application/x-bzip2", CATEGORY_ARCHIVE, ".tar.bz2")
