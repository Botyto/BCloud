from dataclasses import dataclass
import io
import logging
import pickle
from typing import List

from .tools import fspath
from .tools.errors import FileAlreadyExists
from .tools.files import FileManager
from .tools.storage import StorageManager

from core.data.blobs.base import OpenMode
from core.data.sql.database import Session
from miniapps.profile.importing.google import GoogleImporter, GoogleImportingContext

from googleapiclient.http import MediaIoBaseDownload

logger = logging.getLogger(__name__)


@dataclass
class DriveFile:
    id: str
    path: str
    mime: str


class DriveExport:
    mime: str
    ext: str

    def __init__(self, mime: str, ext: str):
        assert ext.startswith("."), "Extension must start with a dot"
        self.mime = mime
        self.ext = ext


class DriveFileContext(GoogleImportingContext):
    i: int
    n: int
    files: FileManager
    session: Session
    path: str
    gfile: DriveFile

    def __init__(self,
        base: GoogleImportingContext,
        i: int, n: int,
        files: FileManager, session: Session,
        path: str, gfile: DriveFile
    ):
        self._extend(base)
        self.i = i
        self.n = n
        self.files = files
        self.session = session
        self.path = path
        self.gfile = gfile

    @property
    def mime(self):
        return self.gfile.mime
    
    @property
    def google_id(self):
        return self.gfile.id
    
    @property
    def file_n(self):
        return f"{self.i + 1}/{self.n}"


class GoogleDriveImporter(GoogleImporter):
    NAME = "drive"
    SERVICE = "drive"
    VERSION = "v3"
    SCOPES = {
        "https://www.googleapis.com/auth/drive.metadata.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    }

    PHOTOS_NAMES = {"Google Photos", "Google Фото"}

    def __gather_files(self, output: list, context: GoogleImportingContext, parent="root", path=""):
        query = f"'{parent}' in parents and trashed = false"
        fields = "nextPageToken, files(id, name, mimeType, shortcutDetails)"
        results = context.service.files().list(q=query, pageSize=100, fields=fields).execute()  # type: ignore
        items = results.get("files", [])
        for item in items:
            if item["name"] in self.PHOTOS_NAMES and parent == "root":
                continue
            item_path = f"{path}/{item['name']}"
            output.append(DriveFile(item["id"], item_path, item["mimeType"]))
            if item["mimeType"] == "application/vnd.google-apps.folder":
                self.__gather_files(output, context, item["id"], item_path)
            elif item["mimeType"] == "application/vnd.google-apps.shortcut":
                target_id = item['shortcutDetails']['targetId']
                target_mime = item['shortcutDetails']['targetMimeType']
                if target_mime == "application/vnd.google-apps.folder":
                    self.__gather_files(output, context, target_id, item_path)
                else:
                    output.append(DriveFile(target_id, item_path, target_mime))

    STORAGE_NAME = "Google Drive"
    def __get_gdrive_storage(self, context: GoogleImportingContext, session: Session):
        storages = StorageManager(context.user_id, session)
        gdrive_storages = storages.by_name(self.STORAGE_NAME)
        if gdrive_storages:
            return gdrive_storages[0]  # type: ignore
        return storages.create(self.STORAGE_NAME)
    
    OD_SPREADSHEET_EXP = DriveExport("application/x-vnd.oasis.opendocument.spreadsheet", ".ods")
    OD_TEXT_EXP = DriveExport("application/vnd.oasis.opendocument.text", ".odt")
    OD_PRESENTATION_EXP = DriveExport("application/vnd.oasis.opendocument.presentation", ".odp")
    MAP_EXP = DriveExport("application/vnd.google-earth.kmz", ".kmz")
    PDF_EXP = DriveExport("application/pdf", ".pdf")
    def __import_file(self, context: DriveFileContext):
        match context.mime:
            case "application/vnd.google-apps.folder":
                logger.debug("Creating directory %s - %s", context.file_n, context.path)
                return self.__import_dir(context)
            case "application/vnd.google-apps.spreadsheet":
                return self.__import_download(context, self.OD_SPREADSHEET_EXP)
            case "application/vnd.google-apps.document":
                return self.__import_download(context, self.OD_TEXT_EXP)
            case "application/vnd.google-apps.presentation":
                return self.__import_download(context, self.OD_PRESENTATION_EXP)
            case "application/vnd.google-apps.map":
                return self.__import_download(context, self.MAP_EXP)
            case "application/vnd.google-apps.drawing":
                return self.__import_download(context, self.PDF_EXP)
            case _:
                return self.__import_download(context, None)

    def __import_dir(self, context: DriveFileContext):
        context.files.makedirs(fspath.dirname(context.path))
        context.session.commit()

    def __import_download(self, context: DriveFileContext, export: DriveExport|None):
        try:
            logger.debug("Downloading file %s - %s", context.file_n, context.path)
            try:
                final_path = context.path
                if export is not None:
                    request = context.service.files().export_media(fileId=context.google_id, mimeType=export.mime)  # type: ignore
                    final_path += export.ext
                else:
                    request = context.service.files().get_media(fileId=context.google_id)  # type: ignore
                context.files.makedirs(fspath.dirname(final_path))
                context.session.commit()
                file = context.files.makefile(final_path, context.mime)
                buffer = io.BytesIO()
                downloader = MediaIoBaseDownload(buffer, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                context.files.contents.write(file, buffer.getvalue())
            except Exception as e:
                logger.debug("Failed to download file %s - %s", context.file_n, str(e))
                return
            logger.debug("Finished downloading file %s", context.file_n)
            context.session.commit()
        except FileAlreadyExists:
            return  # file already downloaded/exists

    def __download_files(self, gfiles: List[DriveFile], context: GoogleImportingContext):
        logger.debug("Downloading %d files", len(gfiles))
        with context.database.make_session() as session:
            storage = self.__get_gdrive_storage(context, session)
            files = FileManager(context.blobs, context.user_id, session)
            for i, gfile in enumerate(gfiles):
                path = fspath.join(storage.id, gfile.path)
                gfile_context = DriveFileContext(context, i, len(gfiles), files, session, path, gfile)
                self.__import_file(gfile_context)

    def __debug_gfiles(self, job_id: int):
        with open(f"tempdata/asyncjobs/{job_id}/gdrive_import/files.pickle", "rb") as fh:
            gfiles = pickle.load(fh)
        import csv
        with open(f"tempdata/asyncjobs/{job_id}/gdrive_import/files.csv", "wt", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=["id", "path", "mime"])
            writer.writeheader()
            for gfile in gfiles:
                writer.writerow({
                    "id": gfile.id,
                    "path": gfile.path,
                    "mime": gfile.mime,
                })

    async def run(self, context: GoogleImportingContext):
        files: List[DriveFile] = []
        cache_addr = context.temp_file_addr("gdrive_import", f"files.pickle")
        if context.blobs.exists(cache_addr):
            logger.debug("Loading cached files")
            with context.blobs.open(cache_addr, OpenMode.READ) as fh:
                files = pickle.load(fh)
        else:
            logger.debug("Gethering files")
            self.__gather_files(files, context)
            files.sort(key=lambda f: f.path)
            with context.blobs.open(cache_addr, OpenMode.WRITE) as fh:
                pickle.dump(files, fh)
        self.__download_files(files, context)
        logger.debug("Finished importing")
        # TODO delete cache file
