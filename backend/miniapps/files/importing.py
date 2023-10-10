from dataclasses import dataclass
import logging
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


class GoogleDriveImporter(GoogleImporter):
    SERVICE = "drive"
    SCOPES = {"https://www.googleapis.com/auth/drive.metadata.readonly"}

    PHOTOS_NAMES = {"Google Photos", "Google Фото"}

    def __gather_files(self, output: list, context: GoogleImportingContext, parent="root", path=""):
        query = f"'{parent}' in parents and trashed = false"
        fields = "nextPageToken, files(id, name, mimeType)"
        results = context.service.files().list(q=query, pageSize=100, fields=fields).execute()  # type: ignore
        items = results.get("files", [])
        for item in items:
            if item["name"] in self.PHOTOS_NAMES and parent == "root":
                continue
            item_path = f"{path}/{item['name']}"
            output.append(DriveFile(
                id=item["id"],
                path=item_path,
                mime=item["mimeType"],
            ))
            if item["mimeType"] == "application/vnd.google-apps.folder":
                self.__gather_files(output, context, item["id"], item_path)

    def __get_gdrive_storage(self, context: GoogleImportingContext, session: Session):
        storages = StorageManager(context.user_id, session)
        gdrive_storages = storages.by_name("Google Drive")
        if gdrive_storages:
            return gdrive_storages[0]
        return storages.create("Google Drive")

    def __download_files(self, gfiles: List[DriveFile], context: GoogleImportingContext):
        logger.debug("Downloading %d files", len(gfiles))
        with context.database.make_session() as session:
            storage = self.__get_gdrive_storage(context, session)
            files = FileManager(context.files, context.user_id, session)
            for i, gfile in enumerate(gfiles):
                if gfile.mime == "application/vnd.google-apps.folder":
                    continue
                path = fspath.join(storage.id, f"/{gfile.path}")
                try:
                    files.makedirs(fspath.dirname(path))
                    file = files.makefile(path, gfile.mime)
                    logger.debug("Downloading file %d/%d", i + 1, len(gfiles))
                    media = context.service.files().get_media(fileId=gfile.id)  # type: ignore
                    with files.contents.open(file, OpenMode.WRITE) as fh:
                        downloader = MediaIoBaseDownload(fh, media)
                        done = False
                        while not done:
                            status, done = downloader.next_chunk()
                        logger.debug("Finished downloading file %d/%d", i + 1, len(gfiles))
                except FileAlreadyExists:
                    continue  # file already downloaded/exists

    async def run(self, context: GoogleImportingContext):
        files: List[DriveFile] = []
        logger.debug("Gethering files")
        self.__gather_files(files, context)
        files.sort(key=lambda f: f.path)
        self.__download_files(files, context)
        logger.debug("Finished importing")
