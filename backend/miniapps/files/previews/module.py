from .archives import ArchiveFileList, ArchivePreview

from ..tools.files import FileManager

from core.api.modules.rest import ApiResponse, RestMiniappModule, get
from core.api.modules.gql import GqlMiniappModule, query
from core.auth.handlers import AuthError
from core.data.blobs.base import OpenMode


class PreviewModule(GqlMiniappModule):
    _manager: FileManager|None = None

    @property
    def manager(self):
        if self._manager is None:
            if self.user_id is None:
                raise AuthError()
            self._manager = FileManager(self.context.blobs, self.user_id, self.session)
        return self._manager

    @query()
    def archive(self, path: str) -> ArchiveFileList:
        file = self.manager.by_path(path)
        if file is None:
            raise FileNotFoundError(path)
        with self.manager.contents.open(file, OpenMode.READ) as blob:
            return ArchivePreview.list_files(blob)


class PreviewContentsModule(RestMiniappModule):
    _manager: FileManager|None = None

    @property
    def manager(self):
        if self._manager is None:
            if self.user_id is None:
                raise AuthError()
            self._manager = FileManager(self.context.blobs, self.user_id, self.session)
        return self._manager

    @get("/api/files/preview/(.*)", name="files.preview.read")
    def archive_file(self, path: str):
        file = self.manager.by_path(path)
        if file is None:
            raise FileNotFoundError(path)
        with self.manager.contents.open(file, OpenMode.READ) as blob:
            file_contents = ArchivePreview.read_file(blob, path)
            response = ApiResponse()
            response.content = file_contents.data
            response.add_header("Content-Type", file_contents.mime or "application/octet-stream")
            return response
