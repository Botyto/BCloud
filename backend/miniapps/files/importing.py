from dataclasses import dataclass
import io
import logging
from typing import List

from googleapiclient.http import MediaIoBaseDownload

from .data import FileStorage
from .tools import fspath
from .tools.errors import FileAlreadyExists
from .tools.files import FileManager
from .tools.storage import StorageManager

from core.data.sql.database import Session

from miniapps.profile.importing.google import GoogleImporter, GoogleImportingContext
from miniapps.profile.importing.google_items import GoogleItem, GoogleItemContext, GoogleItemImporter

logger = logging.getLogger(__name__)


class DriveExport:
    mime: str
    ext: str

    def __init__(self, mime: str, ext: str):
        assert ext.startswith("."), "Extension must start with a dot"
        self.mime = mime
        self.ext = ext


@dataclass
class GFile(GoogleItem):
    id: str
    path: str
    mime: str

    @property
    def google_name(self):
        return self.id


@dataclass
class DriveHelper:
    storage: FileStorage
    manager: FileManager


class DriveItemImporter(GoogleItemImporter[GFile, DriveHelper]):
    ITEM_NAME = "file"
    PAGINATED = False

    PHOTOS_NAMES = {"Google Photos", "Google Фото"}
    def gather(self, output: List[GFile], parent="root", path=""):
        query = f"'{parent}' in parents and trashed = false"
        fields = "nextPageToken, files(id, name, mimeType, shortcutDetails)"
        results = context.service.files().list(q=query, pageSize=100, fields=fields).execute()  # type: ignore
        items = results.get("files", [])
        for item in items:
            if item["name"] in self.PHOTOS_NAMES and parent == "root":
                continue
            item_path = f"{path}/{item['name']}"
            output.append(GFile(item["id"], item_path, item["mimeType"]))
            if item["mimeType"] == "application/vnd.google-apps.folder":
                self.gather(output, item["id"], item_path)
            elif item["mimeType"] == "application/vnd.google-apps.shortcut":
                target_id = item['shortcutDetails']['targetId']
                target_mime = item['shortcutDetails']['targetMimeType']
                if target_mime == "application/vnd.google-apps.folder":
                    self.gather(output, target_id, item_path)
                else:
                    output.append(GFile(target_id, item_path, target_mime))

    STORAGE_NAME = "Google Drive"
    def __get_gdrive_storage(self, context: GoogleImportingContext, session: Session):
        storages = StorageManager(context.user_id, session)
        gdrive_storages = storages.by_name(self.STORAGE_NAME)
        if gdrive_storages:
            return gdrive_storages[0]  # type: ignore
        return storages.create(self.STORAGE_NAME)

    def create_helper(self, session: Session):
        return DriveHelper(
            storage=self.__get_gdrive_storage(self.context, session),
            manager=FileManager(self.context.blobs, self.context.user_id, session),
        )

    OD_SPREADSHEET_EXP = DriveExport("application/x-vnd.oasis.opendocument.spreadsheet", ".ods")
    OD_TEXT_EXP = DriveExport("application/vnd.oasis.opendocument.text", ".odt")
    OD_PRESENTATION_EXP = DriveExport("application/vnd.oasis.opendocument.presentation", ".odp")
    MAP_EXP = DriveExport("application/vnd.google-earth.kmz", ".kmz")
    PDF_EXP = DriveExport("application/pdf", ".pdf")
    def import_item(self, gitem_context: GoogleItemContext[GFile, DriveHelper]):
        path = fspath.join(gitem_context.helper.storage.id, gitem_context.item.path)
        match gitem_context.item.mime:
            case "application/vnd.google-apps.folder":
                logger.debug("Creating directory %s - %s", gitem_context.item_num, path)
                return self.__import_dir(gitem_context, path)
            case "application/vnd.google-apps.spreadsheet":
                return self.__import_download(gitem_context, path, self.OD_SPREADSHEET_EXP)
            case "application/vnd.google-apps.document":
                return self.__import_download(gitem_context, path, self.OD_TEXT_EXP)
            case "application/vnd.google-apps.presentation":
                return self.__import_download(gitem_context, path, self.OD_PRESENTATION_EXP)
            case "application/vnd.google-apps.map":
                return self.__import_download(gitem_context, path, self.MAP_EXP)
            case "application/vnd.google-apps.drawing":
                return self.__import_download(gitem_context, path, self.PDF_EXP)
            case _:
                return self.__import_download(gitem_context, path, None)
            
    def __import_dir(self, gitem_context: GoogleItemContext[GFile, DriveHelper], path: str):
        gitem_context.helper.manager.makedirs(fspath.dirname(path))
        gitem_context.session.commit()

    def __import_download(self, gitem_context: GoogleItemContext[GFile, DriveHelper], path: str, export: DriveExport|None):
        try:
            logger.debug("Downloading file %s - %s", gitem_context.item_num, path)
            try:
                final_path = path
                if export is not None:
                    request = gitem_context.service.files().export_media(fileId=gitem_context.google_id, mimeType=export.mime)  # type: ignore
                    final_path += export.ext
                else:
                    request = gitem_context.service.files().get_media(fileId=gitem_context.google_id)  # type: ignore
                gitem_context.helper.manager.makedirs(fspath.dirname(final_path))
                gitem_context.session.commit()
                file = gitem_context.helper.manager.makefile(final_path, gitem_context.item.mime)
                buffer = io.BytesIO()
                downloader = MediaIoBaseDownload(buffer, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                gitem_context.helper.manager.contents.write(file, buffer.getvalue())
            except Exception as e:
                logger.debug("Failed to download file %s - %s", gitem_context.item_num, str(e))
                return
            logger.debug("Finished downloading file %s", gitem_context.item_num)
            gitem_context.session.commit()
        except FileAlreadyExists:
            return  # file already downloaded/exists


class GoogleDriveImporter(GoogleImporter):
    NAME = "drive"
    SERVICE = "drive"
    VERSION = "v3"
    SCOPES = {
        "https://www.googleapis.com/auth/drive.metadata.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    }

    async def run(self, context: GoogleImportingContext):
        drive = DriveItemImporter(logger, context)
        await drive.run()
