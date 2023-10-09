from dataclasses import dataclass
from typing import cast

from googleapiclient.discovery import Resource

from miniapps.profile.importing.google import GoogleImporter, GoogleImportingContext


@dataclass
class DriveFile:
    id: str
    path: str
    mime: str


class GoogleDriveImporter(GoogleImporter):
    SERVICE = "drive"
    SCOPES = {"https://www.googleapis.com/auth/drive.metadata.readonly"}

    PHOTOS_NAMES = {"Google Photos", "Google Фото"}

    def __gather_files(self, output: list, service: Resource, parent="root", path=""):
        query = f"'{parent}' in parents and trashed = false"
        fields = "nextPageToken, files(id, name, mimeType)"
        results = service.files().list(q=query, pageSize=100, fields=fields).execute()
        items = results.get('files', [])
        for item in items:
            if item['name'] in self.PHOTOS_NAMES and parent == "root":
                continue
            item_path = f"{path}/{item['name']}"
            output.append(DriveFile(
                id=item["id"],
                path=item_path,
                mime=item["mimeType"],
            ))
            if item["mimeType"] == "application/vnd.google-apps.folder":
                self.__gather_files(output, service, item["id"], item_path)

    async def run(self, context: GoogleImportingContext):
        files = []
        service = cast(Resource, context.service)
        self.__gather_files(files, service)
        print(files)
